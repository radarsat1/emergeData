#!/usr/bin/env python

# Extract some characteristic curves describing the data.

from pylab import *
from scipy.signal import *
from scipy.interpolate import interp1d
from scikits.audiolab import Sndfile, Format
from read_minibees import read_minibees, mag
from export_audio import find_offsets, split_data_on_offsets

import sys

def linspacerize(t, x, n):
    m = x
    f = interp1d(t, m)
    ft = arange(n)/float(n)*(t[-1]-t[0]) + t[0]
    return ft, f(ft)

def plot_rms(t, x):
    ft, fx = linspacerize(t, x[:,0], 1000)
    avg = filtfilt(*butter(1, 0.01, 'low'), x=fx)
    rms = filtfilt(*butter(1, 0.01, 'low'), x=sqrt((fx-avg)**2))

    pt = [0]
    for k in xrange(len(ft)-1):
        def zero():
            x1 = ft[k];   y1 = fx[k]-avg[k+1]
            x2 = ft[k+1]; y2 = fx[k+1]-avg[k+1]
            return (x1*y2-x2*y1)/(y2-y1)
        z = zero()
        if (fx[k+1] > avg[k+1]
            and fx[k] < avg[k+1]
            and (z - pt[-1]) > 0.001):  # Frequency limit = 1000 Hz
            pt.append(z)

    freqs = 1.0/clip(array(pt[1:])-array(pt[:-1]), 0.001, 100000)
    lft, lfreqs = linspacerize(pt[1:], freqs, 1000)
    ffreqs = filtfilt(*butter(1, 0.01, 'low'), x=lfreqs*20)

    clf()
    plot(ft, fx, '#DDDDDD')
    plot(ft, avg, label='running mean')
    plot(ft, rms, label='running rms')
    plot(lft, ffreqs, label='avg freq * 20')
    xlabel('time (min)')
    legend()

if __name__=="__main__":
    minibees, fields = read_minibees()

    for n in {10:minibees[10]}:
        data = minibees[n]
        offsets = find_offsets(data)
        d = split_data_on_offsets(data, offsets)
        # [plot_rms(a[9600:10200,4], a[9600:10200,5:8])
        #  for a in d if a.shape[0]>10200]
        plot_rms((d[1][:,4]-d[1][0,4])/30.0/60.0, d[1][:,5:8])

    show()
