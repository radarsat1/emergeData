#!/usr/bin/env python

__all__ = ['magnitude']

from numpy import sqrt, array
from scipy.signal import lfilter, butter

def magnitude(d):
    if d.has_key('mag'): return
    a = d['accel']
    d['mag'] = sqrt(a[:,0]*a[:,0] + a[:,1]*a[:,1] + a[:,2]*a[:,2])
    return d

def hipassed(d,o,c):
    if d.has_key('hipassed'): return
    a = d['accel']
    b = butter(o,c,'high')
    d['hipassed'] = array([lfilter(b[0], b[1], a[:,0]),
                           lfilter(b[0], b[1], a[:,1]),
                           lfilter(b[0], b[1], a[:,2])]).T
    return d
