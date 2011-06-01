#!/usr/bin/env python

"""Extract some characteristic curves describing the data."""

__all__ = ['calc_curves']

from pylab import *
from scipy.signal import *
from scipy.interpolate import interp1d
from scikits.audiolab import Sndfile, Format
from export_audio import find_offsets, split_data_on_offsets

import sys

def linspacerize(t, x, n):
    m = x
    f = interp1d(t, m)
    ft = arange(n)/float(n)*(t[-1]-t[0]) + t[0]
    return ft, f(ft)

def calc_curves(t, x, c):
    L = len(t)*10
    srL = L / (t[-1]-t[0])
    ft, fx = linspacerize(t, x, L)
    avg = filtfilt(*butter(1, c/srL, 'low'), x=fx)
    rms = filtfilt(*butter(1, c/srL, 'low'), x=sqrt((fx-avg)**2))

    pt = [0]
    for k in xrange(len(ft)-1):
        def zero():
            x1 = ft[k];   y1 = fx[k]-avg[k+1]
            x2 = ft[k+1]; y2 = fx[k+1]-avg[k+1]
            return (x1*y2-x2*y1)/(y2-y1)
        z = zero()
        if (fx[k+1] > avg[k+1]
            and fx[k] < avg[k+1]
            and (z - pt[-1]) > 1000.0/srL):  # Frequency limit = 1000 Hz
            pt.append(z)

    freqs = 1.0/clip(array(pt[1:])-array(pt[:-1]), 0.001, 100000)
    lft, lfreqs = linspacerize(pt[1:], freqs, L)
    ffreqs = filtfilt(*butter(1, c/srL, 'low'), x=lfreqs)

    # Periodicity is defined here as "average absolute difference
    # between instantaneous frequency and running mean frequency."
    pfreqs = filtfilt(*butter(1, c/srL, 'low'), x=abs(lfreqs-ffreqs))
    periodicity = (max(pfreqs)-pfreqs) / max(pfreqs)

    return {'time': ft,
            'y': fx,
            'avg': avg,
            'rms': rms,
            'freq': ffreqs,
            'periodicity': periodicity}

def plot_curves(t, x):
    curves = calc_curves(t, x, 0.1)
    clf()
    plot(curves['time'], curves['y'], '#DDDDDD')
    plot(curves['time'], curves['avg'], label='running mean')
    plot(curves['time'], curves['rms'], label='running rms')
    plot(curves['time'], curves['freq'], label='avg freq')
    plot(curves['time'], curves['periodicity']*200, label='periodicity')
    xlabel('time (min)')
    legend()

if __name__=="__main__":
    from read_minibees import read_minibees, mag
    minibees, fields = read_minibees()

    for n in {10:minibees[10]}:
        data = minibees[n]
        offsets = find_offsets(data)
        d = split_data_on_offsets(data, offsets)
        # [plot_rms(a[9600:10200,4], a[9600:10200,5])
        #  for a in d if a.shape[0]>10200]
        plot_curves((d[1][:,4]-d[1][0,4])/30.0, d[1][:,5])

    show()
