import argparse
import numpy as np
from scipy.io import wavfile
import scipy.signal
import matplotlib.pyplot as plt


class DTMF(object):
    def __init__(self, filename):
        self.dtmf_table = {
            '1': [697, 1209],
            '2': [697, 1336],
            '3': [697, 1477],
            '4': [770, 1209],
            '5': [770, 1336],
            '6': [770, 1477],
            '7': [852, 1209],
            '8': [852, 1336],
            '9': [852, 1477],
            '0': [941, 1336],
        }

        self.t = 0.04  # process by T seconds intervals
        # Stores the data as well as the sample rate read from the file
        self.sample_rate, self.data = wavfile.read(filename)

        # print(f"number of channels = {self.data.shape[0]}")
        self.length = self.data.shape[0] / self.sample_rate
        print(f"length = {self.length}s")


        if len(self.data.shape) == 2:
            self.data = self.data.sum(axis=1)

        # Stores the step value
        self.step = int(len(self.data) // (len(self.data) / self.sample_rate // self.t))
        # Stores the final string of number the audio contains
        self.char_str = ""

    @staticmethod
    def match(fourier, frequencies, lower_bound, higher_bound, array):
        # where(condition, [x, y]) Return elements chosen from `x` or `y` depending on `condition`.
        begin = np.where(frequencies > lower_bound)[0][0]
        end = np.where(frequencies > higher_bound)[0][0]

        freq = frequencies[begin:end]  # frequency
        m_range = abs(fourier.real[begin:end])  # amplitude

        ret_freq = freq[np.where(m_range == max(m_range))[0][0]]

        error = 15 # acceptable frequency error in hertz
        closest = 0

        for f in array:
            if abs(ret_freq - f) < error:
                error = abs(ret_freq - f)
                closest = f

        return closest

    def decode(self):
        c = ""
        for i in range(0, len(self.data) - self.step, self.step):
            signal = self.data[i:i + self.step]

            fourier = np.fft.fft(signal)  # amplitude
            # Given a window length `n` and a sample spacing `d`
            frequencies = np.fft.fftfreq(signal.size,  d=(1 / self.sample_rate))

            low_freq = self.match(fourier, frequencies, 0, 960, [697, 770, 852, 941])
            high_freq = self.match(fourier, frequencies, 1180, 1500, [1209, 1336, 1477])

            if low_freq == 0 or high_freq == 0:
                c = ""
                continue
            for val, pair in self.dtmf_table.items():
                if low_freq == pair[0] and high_freq == pair[1]:
                    if val != c:
                        c = val
                        self.char_str += c
        return self.char_str




parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType('r'))
parser.add_argument("-p", "--plot", help="show graphs to debug", action="store_true")

args = parser.parse_args()
file = args.file.name  # enter filename when entering command to launch program
try:
    fps, data = wavfile.read(file)   #using library scipy https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
except FileNotFoundError:
    print("No such file:", file)
    exit()
except ValueError:
    print("Impossible to read:", file)
    print("Please give a wav file.")
decoder = DTMF(file)
dtfm = decoder.decode()

for i in dtfm:
    print(i, sep=' ', end='', flush=True)
