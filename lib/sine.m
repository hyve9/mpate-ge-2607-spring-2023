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
