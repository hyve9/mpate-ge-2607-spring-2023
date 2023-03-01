% 1.a Make a sine wave
fs = 44100;
t = [0:fs-1]/fs;
f = 15;

function [x] = sine(f, fs, t, A, p)
%
% Generates a signal based on a frequency. Optional sample rate, time, amplitude, phase.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  if (~exist('fs', 'var') || isempty(fs))
    fs = 44100;
  endif
  if (~exist('t', 'var') || isempty(t))
    t = [0:fs*5-1]/fs;
  endif
  if (~exist('A', 'var') || isempty(A))
    A = 1;
  endif
  if (~exist('p', 'var') || isempty(p))
    p = 0;
  endif

  x = A*sin(2*pi*f*t + p);
endfunction

signal = sine(f, fs, t);

figure(1);
plot(t, signal);

function x = bitCrush(input, bitDepth)
%
% Adds harmonic distortion (I think)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  for i = 1:numel(input)
    x(i) = round(input(i) * 2^bitDepth) * 2^-bitDepth;
  endfor
endfunction

% 1.a Distort it a bit

depth = 8;
signal_dist = bitCrush(signal, depth);

figure(2);
plot(t, signal_dist);


% 1.b Add dithering

function x = dither(input, bitDepth)
%
% Dithers (I think)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  for i = 1:numel(input)
    x(i) = input(i) + (rand() * 2^-(bitDepth+1));
  endfor
endfunction

signal_dith = dither(signal_dist, depth);

figure(3);
plot(t, signal_dith);

% 1.c Remove noise in frequency domain

function x = denoise(input)
%
% Denoises (I think)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  y = fft(input);
  samples = length(input);
  for i = 1:numel(y)
    if abs(y(i)).^2/samples < 1  %get the power of each frequency, check if larger than 1
      y(i) = complex(0, imag(y(i))); %if smaller than 1, probably just noise
    endif
  endfor
  x = ifft(y);
endfunction

signal_denoised = denoise(signal_dith);

figure(4);
plot(t, signal_denoised);

% 1.d How to get rid of dithering for the original input signal?
%
% Ans: I think the same denoising algorithm would be capable of removing dithering of the original input signal, but the power of 1 is taken for granted.
% Instead, a frequency gate based on "relative" power instead of a hard cap at 1 might be more effective at removing dithering.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 2. Write a dynamic compression algorithm

function x = dynCompressor(input, threshold, slope, gain)
%
% Applies dynamic compression. Takes threshold, slope, input. Optional gain matching.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  if (~exist('gain', 'var') || isempty(gain))
    gain = 0.1;
  endif

  for i = 1:numel(input)
    if input(i) > threshold
      x(i) = slope * input(i) + gain;
    elseif input(i) < -threshold
      x(i) = slope * input(i) - gain;
    else
      x(i) = input(i);
    endif
  endfor
endfunction

% Uncompressed
figure(5);
subplot(2, 1, 1);
plot(t, signal);

% Compressed
threshold = 0.8;
slope = 0.5;
signal_compressed = dynCompressor(signal, threshold, slope);
subplot(2, 1, 2);
plot(t, signal_compressed);

function [frange, power] = plotfft(input, fs)
%
% Plots fft according to https://www.mathworks.com/help/matlab/math/basic-spectral-analysis.html
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  y = fft(input);
  n = length(input);
  frange = (0:n-1) * fs/n;
  power = abs(y).^2/n;
endfunction

[frange_orig, power_orig] = plotfft(signal, fs);
[frange_comp, power_comp] = plotfft(signal_compressed, fs);

figure(6);
subplot(2, 1, 1);
plot(frange_orig, power_orig);

subplot(2, 1, 2);
plot(frange_comp, power_comp);

% 3. Write a bit quantizing algorithm
% Note: I think bitCrush() already does this?

% Original
figure(7);
subplot(2, 1, 1);
plot(t, signal);

% Heavy bit quantized
subplot(2, 1, 2);
signal_dist_heavy = bitCrush(signal, 4);
plot(t, signal_dist_heavy);
hold on;

% Error
error = signal - signal_dist_heavy;
plot(t, error);
hold off;

% 4a. Write a chorus filter with no variable delay.

function x = fixedChorus(input, fs, c, amount)
%
%  Creates a chrous effect without variable delay. Args are input, delay coefficient, and delay amount (in ms).
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  initSamples = round(amount/1000 * fs);
  for i = 1:initSamples
    x(i) = input(i);
  endfor
  for i = initSamples+1:numel(input)
    x(i) = input(i) + c*input(i-initSamples);
  endfor
endfunction

% 4b. Write a chorus filter with variable delay.

function x = varChorus(input, fs, c, range, lfoFreq)
%
%  Creates a chrous effect with variable delay. Adds delay range (in ms) and LFO frequency.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  rSamples = round(range/1000 * fs);
  n = length(input);
  lfo = rSamples/2 * sin(2*pi*lfoFreq*[0:1:n]/fs) + rSamples/2;
  for i = 1:rSamples
    x(i) = input(i);
  endfor
  for i = rSamples+1:numel(input)
    x(i) = input(i) + c*input(i-round(lfo(i)));
  endfor
endfunction

% 4c. Write a chorus filter with fractional delay.

function x = fracChorus(input, fs, c, range, lfoFreq)
%
%  Creates a chrous effect with variable delay. Adds delay range (in ms) and LFO frequency.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  rSamples = round(range/1000 * fs);
  n = length(input);
  lfo = rSamples/2 * sin(2*pi*lfoFreq*[0:1:n]/fs) + rSamples/2;
  for i = 1:rSamples
    x(i) = input(i);
  endfor
  for i = rSamples+1:numel(input)
    fDelayA = (ceil(lfo(i)) - lfo(i)) * input(i - floor(lfo(i))); %Get low side of interpolation
    fDelayB = (1 - (ceil(lfo(i)) - lfo(i))) * input(i - ceil(lfo(i))); %Get high side of interpolation
    fDelay = fDelayA + fDelayB; %Combine
    x(i) = input(i) + c*fDelay;
  endfor
endfunction

figure(7);
subplot(2, 2, 1);
plot(t, signal);

subplot(2, 2, 2);
coef = 1;
delay = 25; % milliseconds
fixSignal = fixedChorus(signal, fs, coef, delay);
plot(t, fixSignal)

subplot(2, 2, 3);
range = 40; % milliseconds
lfoFreq = 5; % 5Hz
varSignal = varChorus(signal, fs, coef, range, lfoFreq);
plot(t, varSignal);

subplot(2, 2, 4);
fracSignal = fracChorus(signal, fs, coef, range, lfoFreq);
plot(t, fracSignal);

% 5. Create a 30 second sound sample

% Create bass
fs = 44100;
t = [0:fs*30-1]/fs;
fA = 220;

drone = sine(fA, fs, t);
up = [0:1/(fs*15):1];
for i = 1:numel(up)
  env(i) = up(i);
  env(numel(up)*2-i) = up(i);
endfor
for i = 1:numel(drone);
  drone(i) = env(i) * drone(i);
endfor

% Create melodies?

lt = [0:fs*3-1]/fs;
harm2 = sine(fA*2, fs, lt);
harm3 = sine(fA*3, fs, lt);
harm4 = sine(fA*4, fs, lt);
harm5 = sine(fA*5, fs, lt);
harm6 = sine(fA*6, fs, lt);
for i = 1:numel(harm2)
  drone(i) = drone(i) + harm2(i);
endfor
distHarm6 = bitCrush(harm6, 4);
for i = numel(harm2)+1:(numel(harm2)*2)
  if i == (numel(harm2)*2)
    drone(i) = drone(i) + distHarm6(length(distHarm6));
  else
    drone(i) = drone(i) + distHarm6(mod(i,numel(harm2)));
  endif
endfor
chorusHarm3 = fixedChorus(harm3, fs, coef, 50);
for i = (numel(harm2)*2)+1:(numel(harm2)*3)
  if i == (numel(harm2)*3)
    drone(i) = drone(i) + chorusHarm3(length(chorusHarm3));
  else
    drone(i) = drone(i) + chorusHarm3(mod(i,numel(harm2)*2));
  endif
endfor
distHarm5 = bitCrush(harm5, 2);
for i = (numel(harm2)*3)+1:(numel(harm2)*4)
  if i == (numel(harm2)*4)
    drone(i) = drone(i) + distHarm5(length(distHarm5));
  else
    drone(i) = drone(i) + distHarm5(mod(i,numel(harm2)*3));
  endif
endfor
fracHarm4 = fracChorus(harm4, fs, coef, 40, 8);
for i = (numel(harm2)*4)+1:(numel(harm2)*5)
  if i == (numel(harm2)*5)
    drone(i) = drone(i) + fracHarm4(length(fracHarm4));
  else
    drone(i) = drone(i) + fracHarm4(mod(i,numel(harm2)*4));
  endif
endfor

threshold = 0.9;
slope = 0.8;
finalSound = dynCompressor(drone, threshold, slope);

figure(8);
plot(t, finalSound);

audiowrite('final.wav', finalSound, fs);


