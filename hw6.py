import numpy as np
import scipy as sp
import sys
import logging
import argparse
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

fmax = 20000

def sine(a, f, fs, ts, te):
    t = np.arange(fs * ts, fs * te)/fs
    return np.sin(2 * np.pi * f * t)

#Envelope?
def jcFreqMod(ac, fc, am, fm, fs, ts, te):
    plt.plot(t, x)
    plt.show()
    plt.plot(t, xs)
    plt.show()
    quit()
    t = np.arange(fs * ts, fs * te)/fs
    y = ac * np.cos(2 * np.pi * fc * t + (am/fm * np.sin(2 * np.pi * fm * t)))
    return y

def autocorrelate(x, fs):
    N = round(min(len(x) / 2, 1024))
    acr = np.zeros(N)
    for t in range(N-1):
        acr[t] = sum(x[n]*x[n+t] for n in range(len(x) - N))
    peaks, _ = sp.signal.find_peaks(acr)
    P = np.mean(np.diff(peaks))
    f0 = fs/P
    return f0

def zCross(x, fs):
    seconds = len(x)/fs
    zs = Counter(np.diff(np.sign(x)) != 0)[True]
    f0 = (zs/seconds)/2
    print(seconds)
    return f0


def inverseComb(x, fs):
    N = round(min(len(x) / 2, 1024))
    b = np.zeros(N)
    b[0] = 1
    b[N-1] = 1
    y = sp.signal.lfilter(b, 1, x)
    z = np.fft.fft(y)
    freqs = np.fft.fftfreq(len(z))
    mi = np.argmax(np.abs(z))
    f0 = np.abs(freqs[mi] * fs)
    return f0

def harmonicProductSpectrum(x, fs):
    y_start = np.fft.fft(x)
    y_end = y_start
    N = 5
    downsamples = []
    samples = len(x)
    for i in range(2, N):
        samples = round(len(x)/i)
        downsamples.append(sp.signal.resample(y_start, samples))
    y_end = y_end[:samples]
    for i in range(len(downsamples)):
        downsamples[i] = downsamples[i][:samples]
        y_end *= downsamples[i]
    freqs = np.fft.fftfreq(len(y_end))
    mi = np.argmax(np.abs(y_end))
    f0 = np.abs(freqs[mi] * fs/(N-1))
    return f0

#This also returns the wrong frequency
def cepstrum(x, fs):
    sbar = np.abs(np.fft.ifft(np.log(np.abs(np.fft.fft(x)))))
    quefs = np.fft.fftfreq(sbar.size, d=1/fs)
    min_f = 60
    max_f = 8000
    lim_l = round(len(x)/fs) * min_f
    lim_r = min((round(len(x)/fs) * max_f), len(sbar))
    sbar_ltd = sbar[lim_l:lim_r]
    quefs_ltd = quefs[lim_l:lim_r]
    f0 = fs/quefs_ltd[np.argmax(sbar_ltd)]
    return f0


# This returns the wrong pitch but I have no idea why
def chroma(x, fs):
    y = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x))
    freqs_log =  np.logspace(0, np.log10(max(freqs)*fs), len(freqs))
    fbase = 27.5
    n = 0
    chroma = np.zeros(11)
    while(fbase * 2**(n+1) < max(freqs_log)):
        f = fbase * 2**n
        indices, = np.where(np.isclose(freqs_log, f, rtol=0.0001))
        for i in indices:
            chroma[n%11] += np.abs(y[i])
        n += 1
    pitches = ['a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#']
    mi = np.argmax(chroma)
    p0 = pitches[mi]
    #logging.debug(chroma)
    return p0

if __name__ == '__main__':

    if(sys.version_info.major < 3):
        print('Please use Python 3.x or higher')
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=str, default='warn', help='Log level (choose from debug, info, warning, error and critical)')
    args = parser.parse_args()

    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }


    loglevel = args.log.lower() if (args.log.lower() in levels) else 'warn'
    logging.basicConfig(stream=sys.stderr, level=levels[loglevel], format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    p1_text = '''
    1.Implement John Chowning’s frequency modulation algorithm. Your input arguments
    should include: modulator/carrier frequencies, and envelopes to modulation index as
    well as amplitude. Modulation index is very important as all (?) acoustic instruments
    start with very rich spectra and gradually become less rich over time as per ADSR
    structures. (5 pts)
    '''

    '''
    logging.info(p1_text)

    # Params
    ac = 1
    fc = 20
    am = 5
    fm = 3
    fs = 44100
    ts = 0
    te = 3

    carrier = sine(ac, fc, fs, ts, te)
    modulator = sine(am, fm, fs, ts, te)
    fm_signal = jcFreqMod(ac, fc, am, fm, fs, ts, te)

    # Plotting
    t = np.arange(fs * ts, fs * te) / fs
    fig, axs = plt.subplots(3, 1)
    signals = [carrier, modulator, fm_signal]
    iter = 0
    for signal in [(carrier, 'r', 'carrier'), (modulator, 'b', 'modulator'), (fm_signal, 'm', 'fm_signal')]:
        axs[iter].plot(t, signal[0], color=signal[1], label=signal[2])
        axs[iter].legend()
        iter += 1

    axs[0].set_title("Frequency Modulation")
    plt.show()
    '''

    p2_text = '''
    Write a fundamental frequency estimation via the following methods. (6 pts total)
        a. Autocorrelation
        b. Zero-crossing characteristics
        c. Inverse-comb filtering
        d. Harmonic product spectrum
        e. Cepstrum analysis
        f. Chroma
    '''

    logging.info(p2_text)

    fs = 44100
    f = 4
    t = np.linspace(0, 3, fs, endpoint=False)
    x = np.sin(2 * np.pi * f * t)
    xs = sp.signal.sawtooth(2 * np.pi * f * t)

    f_estimators = [autocorrelate, zCross, inverseComb, harmonicProductSpectrum, cepstrum, chroma]
    for a in f_estimators:
        logging.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        logging.info('Input frequency = ' + str(f))
        logging.info('Estimating with ' + str(a.__name__))
        f0 = a(x, fs)
        logging.info('Estimated frequency (or pitch): ' + str(f0))
