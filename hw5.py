import numpy as np
import scipy as sp
import sys
import logging
import argparse
import matplotlib.pyplot as plt
from collections import Counter

def sine(a, f, fs, ts, te):
    t = np.arange(fs * ts, fs * te)/fs
    return np.sin(2 * np.pi * f * t)

#Envelope?
def jcFreqMod(ac, fc, am, fm, fs, ts, te):
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
    y = np.fft.fft(x)
    N = round(min(len(x) / 2, 1024))
    for i in range(2, N):
        samples = round(len(x)/i)
        y[:samples] = y[:samples] * sp.signal.resample(x, samples)
    freqs = np.fft.fftfreq(len(y))
    mi = np.argmax(np.abs(y))
    f0 = np.abs(freqs[mi] * fs)
    return f0

def cepstrum(x, fs):
    xbar = np.fft.ifft(np.log(np.fft.fft(x)))
    y = np.fft.fft(xbar)
    freqs = np.fft.fftfreq(len(y))
    mi = np.argmax(np.abs(y))
    f0 = np.abs(freqs[mi] * fs)
    return f0

def chroma(x, fs):
    y = np.fft.fft(x)
    #I can't figure it out
    f0 = 440
    return f0

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
    #plt.show()

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
    f = 440
    x = sine(1, 440, 44100, 0, 3)

    f_estimators = [zCross, autocorrelate, harmonicProductSpectrum, cepstrum, chroma, inverseComb]
    for a in f_estimators:
        logging.info('Estimating with ' + str(a.__name__))
        f0 = a(x, fs)
        logging.info('Estimated frequency: ' + str(f0))
