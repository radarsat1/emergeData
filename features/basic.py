#!/usr/bin/env python

__all__ = ['magnitude']

from numpy import sqrt, array, zeros, average
from scipy.signal import lfilter, butter
import inst_correlation

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

def axes_correlation2d(d,freq,delays):
    if d.has_key('axes_cor2d'): return
    if not d.has_key('hipassed'): return
    a = d['hipassed']
    m = max(delays)
    cors = [inst_correlation.inst_correlation_2d(freq, delays)
            for _ in range(3)]
    [c.next() for c in cors]
    result = zeros((len(d['time']), len(delays)))
    for k,_ in enumerate(d['time']):
        j = abs(array(cors[0].send((d['hipassed'][k,0],
                                    d['hipassed'][k,1]))))
        c = average([j
                    ,abs(array(cors[1].send((d['hipassed'][k,1],
                                             d['hipassed'][k,2]))))
                    ,abs(array(cors[2].send((d['hipassed'][k,0],
                                             d['hipassed'][k,2]))))]
                    ,0) # element-wise average
        result[k] = c
    d['axes_cor2d'] = result
    return d
