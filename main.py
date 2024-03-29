#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import argparse

dtmf = {(697, 1209): "1", (697, 1336): "2", (697, 1477): "3", (770, 1209): "4", (770, 1336): "5", (770, 1477): "6",
        (852, 1209): "7", (852, 1336): "8", (852, 1477): "9", (941, 1209): "*", (941, 1336): "0", (941, 1477): "#"}

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--plot", help="show graphs to debug", action="store_true")
parser.add_argument('file', type=argparse.FileType('r'))

args = parser.parse_args()

file = args.file.name
try:
    fps, data = wavfile.read(file)   #using library scipy https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
except FileNotFoundError:
    print("No such file:", file)
    exit()
except ValueError:
    print("Impossible to read:", file)
    print("Please give a wav file.")
    exit()

precision = 0.04

duration = len(data) / fps

step = int(len(data) // (duration // precision))

plot = args.plot

c = ""

if plot:
    print(
        "Warning:\nThe debug mode is very uncomfortable: you need to close each window to continue.\nFeel free to kill the process doing CTRL+C and then close the window.\n")



try:
    for i in range(0, len(data) - step, step):
        signal = data[i:i + step]

        if plot:
            plt.subplot(311)
            plt.subplots_adjust(hspace=0.5)
            plt.title("audio (entire signal)")
            plt.plot(data)
            plt.xticks([])
            plt.yticks([])
            plt.axvline(x=i, linewidth=1, color='red')
            plt.axvline(x=i + step, linewidth=1, color='red')
            plt.subplot(312)
            plt.title("analysed frame")
            plt.plot(signal)
            plt.xticks([])
            plt.yticks([])

        frequencies = np.fft.fftfreq(signal.size, d=1 / fps)
        amplitudes = np.fft.fft(signal)

        # Low
        i_min = np.where(frequencies > 24)[0][0]
        i_max = np.where(frequencies > 960)[0][0]

        freq = frequencies[i_min:i_max]

        amp = abs(amplitudes.real[i_min:i_max])
        lf = freq[np.where(amp == max(amp))[0][0]]
        delta = args.t
        best = 0

        for f in [697, 770, 852, 941]:
            if abs(lf - f) < delta:
                delta = abs(lf - f)
                best = f


        if plot:
            plt.subplot(313)
            plt.title("Fourier transform")
            plt.plot(freq, amp)
            plt.yticks([])
            plt.annotate(str(int(lf)) + "Hz", xy=(lf, max(amp)))

        lf = best

        # High
        i_min = np.where(frequencies > 1180)[0][0]
        i_max = np.where(frequencies > 1500)[0][0]

        freq = frequencies[i_min:i_max]
        amp = abs(amplitudes.real[i_min:i_max])

        hf = freq[np.where(amp == max(amp))[0][0]]
        delta = args.t
        best = 0

        for f in [1209, 1336, 1477, 1633]:
            if abs(hf - f) < delta:
                delta = abs(hf - f)
                best = f

        if plot:
            plt.plot(freq, amp)
            plt.annotate(str(int(hf)) + "Hz", xy=(hf, max(amp)))

        hf = best

        if plot:
            if lf == 0 or hf == 0:
                txt = "Unknown dial tone"
            else:
                txt = str(lf) + "Hz + " + str(hf) + "Hz -> " + dtmf[(lf, hf)]
            plt.xlabel(txt)

        t = int(i // step * precision)

        if t > int((i - 1) // step * precision):
            m = str(int(t // 60))
            s = str(t % 60)
            s = "0" * (2 - len(s)) + s
            print("\n" + m + ":" + s + " ", end='', flush=True)

        if lf == 0 or hf == 0:
            print(".", end='', flush=True)
            c = ""
        elif dtmf[(lf, hf)] != c:
            c = dtmf[(lf, hf)]
            print(c, end='', flush=True)

        if plot:
            plt.show()

    print()

except KeyboardInterrupt:
    print("\nCTRL+C detected: exiting...")