addpath("./lib");
pkg load communications;

% 1. Implement the Schroeder reverb

fs = 44100;
t = [0:fs*5-1]/fs;
f = 10;

signal = sine(f, fs, t);
noisySignal = awgn(signal, 0.2);

% First, allpass and IIR comb

function y = allPass(input, coef, delay, fs)
%
% Creates an allpass filtered signal. Delay is in milliseconds.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  delaySamples = round(delay/1000 * fs);

  for i = 1:numel(input)
    if i - delaySamples < 1
      ff = 0;
      fb = 0;
    else
      ff = input(i - delaySamples);
      fb = y(i - delaySamples);
    endif
    y(i) = coef * input(i) + ff - coef * fb;  % y[n] = a*x[n] + x[n-N] - a*y[n-N]
  endfor
endfunction

function y = iirComb(input, coef, delay, fs)
%
% Creates a feed-back IIR comb filtered signal. Delay is in milliseconds.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  delaySamples = round(delay/1000 * fs);

  for i = 1:numel(input)
    if i - delaySamples < 1
      fb = 0;
    else
      fb = y(i - delaySamples);
    endif
    y(i) = input(i) + coef * fb;  % y[n] = x[n] + a*y[n-L]
  endfor
endfunction


function y = schroederReverb(input, coef, combDelays, allPassDelays, fs)
%
% Uses comb and allpass filters to create Schroeder reverb. Takes two arrays, one with 4 comb delay values, and one with 2 all pass delay values.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  comb1 = iirComb(input, coef, combDelays(1), fs);
  comb2 = iirComb(input, coef, combDelays(2), fs);
  comb3 = iirComb(input, coef, combDelays(3), fs);
  comb4 = iirComb(input, coef, combDelays(4), fs);

  combedSignal = comb1 + comb2 + comb3 + comb4;
  allPass1 = allPass(combedSignal, coef, allPassDelays(1), fs);
  y = allPass(allPass1, coef, allPassDelays(2), fs);
endfunction


figure(1);
subplot(2, 1, 1);
plot(t, signal);

subplot(2, 1, 2);
coef = 1;
combDelays = [29.7, 37.1, 41.1, 43.7];
allPassDelays = [5000, 1700];
sReverbedSignal = schroederReverb(signal, coef, combDelays, allPassDelays, fs);
plot(t, sReverbedSignal);

%
% Why do you think the multiple comb filters and all-pass filter improve the basic
% reverb algorithm – simply using the all-pass filters? Explain.
%
% The comb filters apply different phasing to the signal at different times, which simulate
% different reflection points, for example, in a room. With the multiple different arrival times
% the generated reverb should sound more natural (as if it were an impulse response in an actual room).


%  2. Write a wah-wah pedal

function y = biQuadWah(input, center, Q, gain, fs)
%
% Outputs a fixed wah signal. Takes center frequency, Q (from 0 - 0.99), gain, and sampling rate.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  yd1 = 0;
  yd2 = 0;
  xd2 = 0;
  for i = 1:numel(input)
    if i > 1
      yd1 = y(i - 1);
    endif
    if i > 2
      yd2 = y(i - 2);
      xd2 = input(i - 2);
    endif
    y(i) = gain * input(i) - xd2 + 2 * Q * cos(2*pi*center*(i/fs)) * yd1 - Q^2 * yd2;
  endfor
endfunction

%  3. Write a GUI for the wah-wah pedal

function biQuadGUI()
%
% GUI for biQuadWah()
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  fs = 44100;
  t = [0:fs*5-1]/fs;
  f = 10;
  signal = sine(f, fs, t);
  tMax = round(length(signal)/fs);

  figure(2);
  plot (t, signal);  axis ([0, tMax, -1, 1]);

  qSlider = uicontrol (                    ...
         'style', 'slider',                ...
         'Units', 'normalized',            ...
         'position', [0.1, 0.1, 0.4, 0.1], ...
         'min', 0,                         ...
         'max', 0.99,                        ...
         'value', 0.50,                      ...
         'callback', {@biQuadDisplay}          ...
       );
  gainSlider = uicontrol (                    ...
         'style', 'slider',                ...
         'Units', 'normalized',            ...
         'position', [0.1, 0.1, 0.8, 0.1], ...
         'min', 0,                         ...
         'max', 1,                        ...
         'value', 0.50,                      ...
         'callback', {@biQuadDisplay}          ...
       );

  fCenterSlider = uicontrol (                    ...
         'style', 'slider',                ...
         'Units', 'normalized',            ...
         'position', [0.1, 0.1, 0.6, 0.1], ...
         'min', 20,                         ...
         'max', 22000,                        ...
         'value', 440,                      ...
         'callback', {@biQuadDisplay}          ...
       );

endfunction

function biQuadDisplay(q, gain, fCenter, event)  % this is very broken but I don't know why
  q = get(q, 'value');
  gain = get(gain, 'value');
  fCenter = get(fCenter, 'value');
  fs = 44100;
  t = [0:fs*5-1]/fs;
  f = 10;
  signal = sine(f, fs, t);
  t = [0:length(signal)-1]/fs;
  tMax = round(length(signal)/fs);
  wSignal = biQuadWah(signal, fCenter, q, gain, fs);
  plot(t, wSignal); axis ([0, tMax, -1, 1]);
endfunction


% 5. Write a piece of music.

% Create bass
fs = 44100;
t = [0:fs*30-1]/fs;
fA = 300;

drone = sine(fA, fs, t);
up = [0:1/(fs*15):1];
for i = 1:numel(up)
  env(i) = up(i);
  env(numel(up)*2-i) = up(i);
endfor
for i = 1:numel(drone);
  drone(i) = env(i) * drone(i);
endfor

% Melodies?
lt = [0:fs*10-1]/fs;
harm2 = biQuadWah(sine(fA*2, fs, lt), fA*10, 0.25, 0.5, fs);
harm3 = biQuadWah(sine(fA*3, fs, lt), fA*5, 0.50, 0.5, fs);
harm4 = biQuadWah(sine(fA*4, fs, lt), fA, 0.75, 0.5, fs);
for i = 1:numel(harm2)
  drone(i) = drone(i) + harm2(i);
endfor
for i = numel(harm2)+1:(numel(harm2)*2)
  if i == (numel(harm2)*2)
    drone(i) = drone(i) + harm3(length(harm3));
  else
    drone(i) = drone(i) + harm3(mod(i,numel(harm2)));
  endif
endfor
for i = (numel(harm2)*2)+1:(numel(harm2)*3)
  if i == (numel(harm2)*3)
    drone(i) = drone(i) + harm4(length(harm4));
  else
    drone(i) = drone(i) + harm4(mod(i,numel(harm2)*2));
  endif
endfor

% Final
finalSignal = schroederReverb(drone, coef, combDelays, allPassDelays, fs);
figure(3);
plot(t, finalSignal);

audiowrite('final3.wav', finalSignal, fs);
