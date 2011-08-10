#!/usr/bin/env python

from pylab import *
from read_minibees import read_minibees, mag
from read_tags import read_tags
import scipy.optimize as opt
import scipy.signal as sig
from scipy.interpolate import interp1d

# def load_gestures():
#     from bz2 import BZ2File
#     gestures = []
#     #for g in BZ2File('../../dotminibee/software/gestures.txt.bz2'):
#     for g in BZ2File('gestures.txt.bz2'):
#         d = [float(x) for x in g.split('[')[1].split(']')[0].split(',')]
#         gestures.append(d)
#     return array(gestures)

# data, sr = mag(load_gestures()), 200.0
# fulldata = data
# data = sig.lfilter(*sig.butter(2, 0.1, 'low'),x=fulldata)[::10]
# sr = 200/10

def find_freq(data, sr, start, length, env):
    window = data[start:start+length]
    time = arange(start,start+length)/sr

    offset = average(window)
    amplitude = sqrt(average((window-offset)**2))/0.707

    c = sig.correlate(window*env, window*env, mode='full')
    c = c[c.size/2:]
    for n,cx,px in zip(range(len(c)-1),c[1:],c[:-1]):
        if px < cx:
            c[:n] = zeros(n)
            break
    p = opt.brute(lambda x: x < c.size and x >= 0 and -c[int(x)] or float('inf'), [(0,c.size-1)])[0]

    f = p and 1.0/(p/sr) or 0

    return f

def freq_series(data, sr, hopsize, length):
    env = hamming(length)
    starts = arange((len(data)-length)/hopsize)*hopsize
    freqs = []
    for s in starts:
        freqs.append(find_freq(data, sr, s, length, env))
    return starts, array(freqs)

def plot_f0(data, sr, m, hopsize, L1, L2, smoothing):
    longtime, longfreqs = freq_series(data, sr, 20, L1)
    shorttime, shortfreqs = freq_series(data, sr, 20, L2)

    numfreqs = min(longfreqs.size, shortfreqs.size)
    timefreqs = shorttime[:numfreqs]

    smoothed_longfreqs = sig.filtfilt(*sig.butter(2,smoothing,'low'),
                                       x=longfreqs[:numfreqs])
    smoothed_shortfreqs = sig.filtfilt(*sig.butter(2,smoothing,'low'),
                                        x=shortfreqs[:numfreqs])

    rc('legend',fontsize=8)

    clf()
    subplot(4,1,1)
    title('workshop S.%d autocorrelation %d Hz'%(m,sr))
    plot(timefreqs, longfreqs[:numfreqs])
    plot(timefreqs, smoothed_longfreqs, label='%d f0'%(L1))
    xlim(min(timefreqs),max(timefreqs))
    legend()
    subplot(4,1,2)
    plot(timefreqs, shortfreqs[:numfreqs])
    plot(timefreqs, smoothed_shortfreqs, label='%d f0'%(L2))
    xlim(min(timefreqs),max(timefreqs))
    legend()
    subplot(4,1,3)
    plot(timefreqs, abs(smoothed_longfreqs - smoothed_shortfreqs),
         label='diff f0')
    xlim(min(timefreqs),max(timefreqs))
    legend()
    subplot(4,1,4)
    plot(data, label='rms')
    xlim(min(timefreqs),max(timefreqs))
    legend()

    return smoothed_longfreqs, abs(smoothed_longfreqs - smoothed_shortfreqs)

minibees, fields = read_minibees()
ion()
clf()
draw()

hopsize = 20
smoothing = 0.05
sr = 10.0
L1 = 1000
L2 = 500

final_results = {}
for m in minibees.keys():
    print m
    data = mag(minibees[m][:,5:8])

    final_results[m] = plot_f0(data, sr, m, hopsize, L1, L2, smoothing)

    savefig('workshop_autocorr_10hz_m%d.png'%m)
    draw()

def unwrap_time(time, timediff):
    brks = [n for n,d in enumerate((time[1:]-time[:-1])) if d < -timediff]
    idx = arange(time.size)
    return sum([time] + [(idx > b)*time[b] for b in brks], axis=0)

clf()
time_range = (0,100000000000)
freqs = []
frdiffs = []
for m in minibees.keys():
    time = unwrap_time(minibees[m][:,4]/30.0, 500)
    hoptime = time[:time.size-L1-hopsize:hopsize]
    time_range = (max(time_range[0], hoptime[0]),
                  min(time_range[1], hoptime[-1]))

    subplot(3,1,1)
    plot(hoptime, final_results[m][0], alpha=0.2)
    subplot(3,1,2)
    plot(hoptime, final_results[m][1], alpha=0.2)
    subplot(3,1,3)
    plot(time, mag(minibees[m][:,5:8]), alpha=0.2)

    freqs.append(interp1d(hoptime, final_results[m][0]))
    frdiffs.append(interp1d(hoptime, final_results[m][1]))

times = arange(time_range[0], time_range[1], 0.1)
sumfreq = zeros(times.size)
sumfrdiff = zeros(times.size)
for n in range(len(minibees.keys())):
    sumfreq   += freqs[n](times)
    sumfrdiff += frdiffs[n](times)
sumfreq /= len(minibees.keys())
sumfrdiff /= len(minibees.keys())

subplot(3,1,1)
title('all minibees + average')
plot(times, sumfreq, c='black', label='1000 f0')
legend()
subplot(3,1,2)
plot(times, sumfrdiff, c='black', label='f0 diff')
legend()

savefig('workshop_all_autocorr_f0_10hz.png')
