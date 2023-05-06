import numpy as np
import wave
from scipy import signal

def sine(f, fs, ts, te):
    s = np.arange(fs * ts, fs * te) / fs
    return np.sin(2 * np.pi * f * s)

def ola(x, fs, overlap, factor, w_size=1024, variation=0):
    # Overlap is a fraction from 0.1 to 0.99
    if overlap >= 1 or overlap <= 0:
        raise ValueError('Overlap must be between 0.1 to 0.99')
    hop_size = round(w_size * overlap)
    window = signal.windows.hann(w_size)
    windows = []
    for i in range(0, len(x), hop_size):
        # Add some randomness to hop location
        if variation > 0:
            var_i = i + np.random.randint(-variation, variation)
        else:
            var_i = i
        if var_i + w_size > (len(x) - 1):
            break
        frame = x[var_i:var_i+w_size]
        if len(window) == len(frame):
            w_frame = window * frame
            windows.append(w_frame)
        else:
            windows.append(frame)
    ol_windows = []
    for i in range(0, len(windows) - 1, 2):
        ol_windows.append([v for pair in zip(windows[i], windows[i+1]) for v in pair])
    y = sum(ol_windows, [])
    y = signal.resample(y, factor)
    return sum(ol_windows, [])

def karplus_strong_filter(x, fs, delay):
    y = np.zeros(len(x))
    for i in range(len(x)):
        if i - delay - 1 < 0:
            y[i] = x[i]
        else:
            y[i] = x[i] + 0.5 * (y[i - delay] + y[i - delay - 1])
    return y

# c = 261
# eb = 311
# g = 392
# ab = 103


def make_music():
    fs = 44100
    notes = [261, 311, 392]
    string = []
    for i in range(90):
        signal = sine(notes[i%3], fs, i/3, i+1/3)
        string.extend(karplus_strong_filter(signal, fs, (i%10)))
    ab = sine(103, fs, 0, 10)
    ab_s = sine(103, fs, 10, 20)
    ab_s = ola(ab_s, fs, 0.2, 2, 1024, 10)
    final_sound = ab.extend(ab_s) + string
    with wave.open('hw4_sound', 'w') as file:
        file.writeframesraw(final_sound)
