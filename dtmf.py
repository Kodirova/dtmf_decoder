import numpy as np
import scipy.io.wavfile as sw
import scipy as sc
import scipy.signal as ss
import matplotlib.pyplot as plt
import pandas as pd


class Parameters:
    #                  1209, 1330, 1477, 1590           #class contains encrypting/decrypting codes
    data = {697: ['0', '1', '2', '3'],  # Dataframe to make the dictionary
            770: ['4', '5', '6', '7'],
            852: ['8', '9', 'a', 'b'],
            941: ['c', 'd', 'e', 'f']}
    lower = list(data.keys())
    hx = pd.DataFrame.from_dict(data, orient='index',
                                columns=[1209, 1330, 1477, 1590])
    upper = list(hx.keys())  # information about coding as its hihest, lowest frequencies and arrays of coding values
    highest_freq = max(upper)
    lowest_freq = min(lower)


class Tools:

    def noise(data):
        noise = np.random.uniform(low=-10000, high=10000, size=(sig.frames))  # noise generator for testing
        noised_data = data + noise
        return noised_data

    def bandpass(data, samp):
        pl = Parameters.lowest_freq
        pu = Parameters.highest_freq
        b, a = ss.butter(1, [pl * 0.8, pu * 1.3], 'bandpass',
                         fs=samp)  # this bandpass filter is adaptable its filtering depends on the encoding frequencies
        data_filtered = ss.filtfilt(b, a, data, axis=0)
        return data_filtered

    def approximate(array1, array2, val1,
                    val2):  # as the fourier transform goes with some inaccuracy we need to find frequencies which are most likely encoded
        array1 = np.asarray(array1)
        idx1 = (np.abs(
            array1 - val1)).argmin()  # we use the information from encoding parameters to correct fft errors and find the closest values from Parameters.hx encoding table
        array2 = np.asarray(array2)
        idx2 = (np.abs(array2 - val2)).argmin()
        return array1[idx1], array2[idx2]

    def split(data, treshold,
              frames):  # function to make divide the whole audio and get boundaty indecies of each signal sound segment
        try:
            data = np.array(data)
            data[0] = 0
            y = 0
            f = int(
                frames / 100)  # the frames would be checked by the groups of 1000 to identify loud and silent regions
            beginnings = {}
            endings = {}
            bin_data = np.where(abs(data) > treshold, 1,
                                0)  # it translates arrray with data into binary data to make the regions more distinct
            for x in range(0, f):
                arr = bin_data[x * 1000: (x + 1) * 1000]
                if 1 in arr:
                    bin_data[x * 1000:(x + 1) * 1000] = 1
                    if bin_data[x * 1000 - 1] == 0:
                        y = y + 1
                        beginnings[x] = x * 1000
                    else:
                        if bin_data[x * 1000 - 1] == 1:
                            endings[y] = x * 1000
            return beginnings, endings
        except:
            print('error split')

    def fft(data, frames, beg, end):  # fft method to make fast fourier transform on object's data
        segment_fft = np.abs((sc.fft(data[beg + 2000:end + 2000])) / frames)[0:20000]
        return segment_fft

    def sifter(
            segment_fft):  # sifter separates 2 strongest frequencies from fft data set to ddecode the message in future

        index1 = np.where(segment_fft == np.amax(segment_fft))[0][0]
        segment_fft[index1] = 0
        index2 = np.where(segment_fft == np.amax(segment_fft))[0][0]
        if index1 > index2:
            return index2, index1

        else:
            return index1, index2


class Read:
    # Read class to extract data from the file, needs filename as argument to operate
    def __init__(self, filename):
        self.filename = filename
        self.samp_freq, self.data = sw.read(self.filename)
        self.frames = len(self.data)

    def interval_grabber(
            self):  # method which finds loud regions in dataset to make the further analysis on every segment
        noise_treshold = np.average(
            abs(self.data)) * 2  # puts a treshold which defines whether it is silent region or not
        beg, end = Tools.split(self.data, noise_treshold, self.frames)
        length = len(beg)
        beg = np.asarray(list(beg.values()))
        end = np.asarray(list(end.values()))
        return beg, end, length

    def decode(self):  # method to execute all the methods above in iterative way to get the desired result
        string = {}
        beg, end, length = self.interval_grabber()

        for i in range(0, length):
            segment_fft = Tools.fft(self.data, self.frames, beg[i], end[i])
            index1, index2 = Tools.sifter(segment_fft)
            index1, index2 = Tools.approximate(Parameters.lower, Parameters.upper, index1, index2)
            letter = Parameters.hx[index2][index1]
            string[i] = letter
        string = np.asarray(list(string.values()))
        return string


sig = Read('Python_SaS_test2.wav')  # the driving code
sig.data = Tools.noise(sig.data)
sig.data = Tools.bandpass(sig.data, sig.samp_freq)
data = sig.data
string = sig.decode()