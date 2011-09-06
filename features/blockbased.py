#!/usr/bin/env python

__all__ = ['windowed', 'windowed_by_axis',
           'autocorrelation', 'axes_correlation']

from pylab import correlate, arange, array, sort
from scipy.signal import hanning

def windowed(data, name, f, fname, size=256, hopsize=128):
    d = data[name]
    if len(d.shape)==1:
        ts = arange((d.shape[0]-size)/hopsize)
        t = array([data['time'][t] for t in ts*hopsize])
        res = []
        for k in ts:
            res.append(f(d[k*hopsize:k*hopsize+size]))
        return {'time': t, fname: array(res)}
    elif len(d.shape)==2:
        ts = arange((d.shape[0]-size)/hopsize)
        t = array([data['time'][t] for t in ts*hopsize])
        res = []
        for k in ts:
            res.append(f(d[k*hopsize:k*hopsize+size,:]))
        return {'time': t, fname: array(res)}

def windowed_by_axis(data, name, f, fname, size=256, hopsize=128):
    d = data[name]
    if len(d.shape)==1:
        ts = arange((d.shape[0]-size)/hopsize)
        t = array([data['time'][t] for t in ts*hopsize])
        res = []
        for k in ts:
            res.append(f(d[k*hopsize:k*hopsize+size]))
        return {'time': t, fname: array(res)}
    elif len(d.shape)==2:
        ts = arange((d.shape[0]-size)/hopsize)
        t = array([data['time'][t] for t in ts*hopsize])
        res = []
        for k in ts:
            res.append(array([f(d[k*hopsize:k*hopsize+size,i])
                              for i in range(d.shape[1])]))
        return {'time': t, fname: array(res)}

def autocorrelation(block):
    w = hanning(len(block))
    if len(block.shape)==1:
        b = block*w
        res = correlate(b, b, mode='full')
        return res[res.shape[0]/2:]
    elif len(block.shape)==2:
        res = array([correlate(block[:,i]*w, block[:,i]*w, mode='full')
                     for i in range(block.shape[1])])
        return res[:,res.shape[1]/2:]

def axes_correlation(block):
    w = hanning(len(block))
    if len(block.shape)==2:
        ax = range(block.shape[1])
        pairs = set([tuple(sort(z)) for z in
                     [[x,y] for x in ax for y in ax if x != y]])
        cor = []
        for p in pairs:
            cor.append(correlate(block[:,p[0]]*w, block[:,p[1]]*w,
                                 mode='full'))
        return reduce(lambda x,y:abs(x)+abs(y), cor)
