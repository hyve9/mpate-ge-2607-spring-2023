import numpy as np
import scipy as sp
import sys
import logging
import argparse
import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf

def sine(a, f, fs, ts, te):
    t = np.arange(fs * ts, fs * te)/fs
    return np.sin(2 * np.pi * f * t)

def getFreqAndPhaseResponse(fs, b, a, k):
    t = np.arange(fs * 2)/fs
    # Generate sweep signal
    sweep = sp.signal.chirp(t, f0=0, f1=fs//2, t1=2, method='linear')
    # Equation: y = x[n] + 0.96 * y[n - 10]
    # b coef = 1; a coef = 0.96
    y = np.zeros(len(sweep))
    for n in range(len(sweep)):
        if n < k:
            y[n] = b * sweep[n]
        else:
            y[n] = b * sweep[n] + a * y[n - k]
    Y = np.fft.rfft(y)
    bins = np.fft.rfftfreq(len(y))
    fig, axs = plt.subplots(2)
    fig.subtitle = 'Frequency (top) and Phase (bottom) response'
    axs[0].plot(bins, Y.real)
    axs[1].plot(bins, Y.imag)
    plt.show()
    return

def sineSweepAndPlot(fs, fmax, fstep):
    t = np.arange(fs * 0.5)/fs
    plt.ion()
    plt.xlabel('Frequency in Hz')
    for i in range(0, fmax, fstep):
        sweep = sp.signal.chirp(t, f0=i, f1=i+fstep, t1=0.5, method='linear')
        S_sweep = np.fft.rfft(sweep)
        bins = np.fft.rfftfreq(len(sweep)) * fmax * 2
        plt.plot(bins, np.abs(S_sweep))
        plt.draw()
        plt.pause(0.000001)
        plt.clf()
    return
        
        

def createHihatFromNoise(noise, fs):
    #cfs = [1800, 2800, 3250, 3300, 4000, 4200, 5100, 5500, 6200]
    noise = noise[0:len(noise)//2]
    cfs = [8000, 6500, 9000, 7500, 12000]
    components = []
    for cf in cfs:
        sos = sp.signal.butter(8, [cf - 100, cf + 100], 'bandpass', fs=fs, output='sos')
        filt = sp.signal.sosfilt(sos, noise)
        components.append(filt)
    output = sum(components)
    points = len(output)
    tau = -(points-1) / np.log(0.01)
    window = sp.signal.windows.exponential(points, 0, tau, False)
    return output * window
    
def createSnareFromNoise(noise, fs):
    #cfs = [1800, 2800, 3250, 3300, 4000, 4200, 5100, 5500, 6200]
    cfs = [8000, 6500, 9000, 7500, 12000, 777, 3500, 4000]
    components = []
    for cf in cfs:
        sos = sp.signal.butter(8, [cf - 100, cf + 100], 'bandpass', fs=fs, output='sos')
        filt = sp.signal.sosfilt(sos, noise)
        components.append(filt)
    output = sum(components)
    points = len(output)
    tau = -(points-1) / np.log(0.01)
    window = sp.signal.windows.exponential(points, 0, tau, False)
    return output * window
    
def createKickFromNoise(noise, fs):
    #cfs = [1800, 2800, 3250, 3300, 4000, 4200, 5100, 5500, 6200]
    cfs = [80, 65, 100, 220, 40, 440, 360, 512, 800]
    components = []
    for cf in cfs:
        sos = sp.signal.butter(8, [cf - 20, cf + 20], 'bandpass', fs=fs, output='sos')
        filt = sp.signal.sosfilt(sos, noise)
        components.append(filt)
    output = sum(components)
    points = len(output)
    tau = -(points-1) / np.log(0.01)
    window = sp.signal.windows.exponential(points, 0, tau, False)
    return output * window

def convolve(sineA, sineB, fs):
    size = len(sineA) + len(sineB) + 1
    SA = np.fft.fft(sineA, n=size)
    SB = np.fft.fft(sineB, n=size)
    SC = SA * SB
    output = np.fft.ifft(SC)
    return output.real 

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


    loglevel = args.log.lower() if (args.log.lower() in levels) else 'info'
    logging.basicConfig(stream=sys.stderr, level=levels[loglevel], format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    p1_text = '''
    Write a program that computes the frequency response and phase response of the
    following difference equation:
    y[n] = x[n]+ 0.96 ⋅ y[n − 10]
    Do not use the freqz MATLAB function or any similar off-the-shelf
    function/library, but rather, write it from scratch by actually sweeping the system with
    a sinusoid. In other words, set the input to:
    x[n ] = e jq n
    and compute
    H (e jq )
    a)b)Plot the frequency and phase responses. (2 pts.)
    What kind of filter is it? (1 pt.)
    You can, and probably should check with freqz is your own version is correct.
    '''

    logging.info(p1_text)
    
    fs = 44100
    b = 1
    a = 0.96
    k = 10
    #getFreqAndPhaseResponse(fs, b, a, k)
    
    #print('Ans: This is a feedback, or IIR, filter.')


    p2_text = '''
    Use a combination of filters (e.g. LPF, HPF, BPFs) to filter a broadband signal and
    create a hi-hat sound, kick sound, and snare sound. Sequence them and make a one
    measure pattern. You can use MATLAB to do this – e.g. butter, cheby1,
    cheby2 etc. functions. (2 pts.)
    '''
    
    logging.info(p2_text)
    
    noise = np.random.random(size=fs//2)
    snare = createSnareFromNoise(noise, fs)
    kick = createKickFromNoise(noise, fs)
    hihat = createHihatFromNoise(noise, fs)
    
    sequence = np.zeros(fs * 10)
    for i in np.linspace(0, 8, 32, endpoint=False):
        sequence[int((i*fs)):int((i*fs + len(hihat)))] += hihat
    for i in np.linspace(2, 8, 12, endpoint=False):
        sequence[int((i*fs)):int((i*fs + len(kick)))] += kick
    for i in np.linspace(4.5, 8.5, 4, endpoint=False):
        sequence[int((i*fs)):int((i*fs + len(snare)))] += snare
    #sf.write('seq.wav', sequence, fs)

    p3_text = '''
    Write a program that will create a sine tone which will sweep from 0 Hz to 80k Hz at
    100 Hz intervals with fs = 44.1k Hz. Plot the magnitude of the DFTs (|X|)
    and explain what is going on. Create an animation so that you can see your sinusoid
    moving along the frequency axis and submit a program that shows this. For
    MATLAB, you can use the drawnow function to make animation possible. On your
    figure also plot the frequency value of the sinusoid in the following three units: (1)
    discrete bin number, (2) discrete radian frequency, and (3) frequency in Hz. Make
    sure you consider aliasing when displaying the frequency values. Suggestion in
    MATLAB – plot the various values in their respective values using the text
    function. (3 pts.)
    '''

    logging.info(p3_text)
    
    fmax = 80000
    fstep = 100
    #sineSweepAndPlot(fs, fmax, fstep)
    print('Ans: The fundamental frequency seems to be moving back and forth. This is due to aliasing.\n \
            Because the fundamental reaches above nyquist (fs/2), we start to see the frequency going\n \
            down instead of up, even though we know this is not the case.')
    
    p4_text = '''
    Write the convolution algorithm in the frequency domain using the fft function in
    MATLAB, for example. Use a single window and no overlap – i.e. not STFT. (2 pts.)
    '''
    
    logging.info(p4_text)
    
    a = 0.1
    fA = 200
    fB = 720
    ts = 0
    te = 2
    sineA = sine(a, fA, fs, ts, te)
    sineB = sine(a, fB, fs, ts, te)
    sineC = convolve(sineA, sineB, fs)
    # Fix amplitudes
    sineA = sineA * a
    sineB = sineB * a
    sineC = sineC * a * a
    sf.write('sineA.wav', sineA, fs)
    sf.write('sineB.wav', sineB, fs)
    sf.write('convolvedSineASineB.wav', sineC, fs) 
    
    p5_text = '''
    Use any of the above or concepts to create a 30 second sound example – if music,
    even better! Upload audio file please!
    '''
    
    logging.info(p5_text)
    
    end = 30
    fD = 400
    fE = 438.3
    ts = 0
    te = 2
    sineD = sine(a, fD, fs, ts, te)
    sineE = sine(a, fE, fs, ts, te)
    sineF = convolve(sineD, sineE, fs)
    sineF = sineF * a * a
    music = np.zeros(fs * (end + 2))
    for i in np.linspace(0, end, 128, endpoint=False):
        music[int((i*fs)):int((i*fs + len(hihat)))] += hihat
    for i in np.linspace(2, end, 60, endpoint=False):
        music[int((i*fs)):int((i*fs + len(kick)))] += kick
    for i in np.linspace(2.5, (end + 0.5), 30, endpoint=False):
        music[int((i*fs)):int((i*fs + len(snare)))] += snare 
    points = len(sineA)
    tau = -(points-1) / np.log(0.01)
    window = sp.signal.windows.exponential(points, 0, tau, False)
    for i in np.linspace(8, end, 48, endpoint=False):
        if i % 4 == 0:
            music[int((i*fs)):int((i*fs + len(sineF)))] += sineF * a
        else:
            if (int((i*fs)) - int((i*fs + len(sineA)))) == -88201:
                music[int((i*fs)):int((i*fs + len(sineA)))] += np.append((sineA * window), 0)
            else:  
                music[int((i*fs)):int((i*fs + len(sineA)))] += (sineA * window)
    t = np.arange(fs * 4)/fs 
    sweep = sp.signal.chirp(t, f0=fA, f1=fB, t1=4, method='hyperbolic')
    for i in np.linspace(12, end, 4, endpoint=False):
        if i % 2 == 0:
            sweep = sp.signal.chirp(t, f0=fD, f1=fE*10, t1=4, method='hyperbolic')
            music[int((i*fs)):int((i*fs + len(sweep)))] += sweep * a
        else:
            sweep = sp.signal.chirp(t, f0=fE*10, f1=fD, t1=4, method='hyperbolic')
            music [int((i*fs)):int((i*fs + len(sweep)))] += sweep * a
    sf.write('music.wav', music, fs)
    
    