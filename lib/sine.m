function [x] = sine(f, A, p, fs, sec)
%
% Generates a signal based on a frequency. Optional sample rate, amplitude, and phase.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if (~exist('A', 'var') || isempty(A))
  A = 1;
end

if (~exist('p', 'var') || isempty(p))
  p = 0;
end

if (~exist('fs', 'var') || isempty(fs))
  fs = 44100;
end

if (~exist('sec', 'var') || isempty(sec))
  sec = 5;
end

x = A*sin(2*pi*f*[1:(fs*sec-1)]/fs + p);

end
