#!/usr/bin/env python

__all__ = ['windowed', 'windowed_by_axis',
           'autocorrelation', 'axes_correlation', 'correlation_reduce']

from pylab import *
from scipy.signal import hanning, fftconvolve

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
        v = res[res.shape[0]/2:]
        return v/max(v)
    elif len(block.shape)==2:
        res = array([correlate(block[:,i]*w, block[:,i]*w, mode='full')
                     for i in range(block.shape[1])])
        v = res[:,res.shape[1]/2:]
        return v/max(v)

def axes_correlation(block):
    w = hanning(len(block))
    if len(block.shape)==2:
        ax = range(block.shape[1])
        pairs = set([tuple(sort(z)) for z in
                     [[x,y] for x in ax for y in ax if x != y]])
        cor = []
        for p in pairs:
            cor.append(fftconvolve(block[:,p[0]]*w,
                                   (block[:,p[1]]*w)[::-1],
                                   mode='full'))
        v = reduce(lambda x,y:abs(x)+abs(y), cor)
        return v / v.max()

def axes_fft(block):
    w = hanning(len(block))
    if len(block.shape)==2:
        ax = range(block.shape[1])
        pairs = set([tuple(sort(z)) for z in
                     [[x,y] for x in ax for y in ax if x != y]])

        normalize = lambda x: ((x - x.mean())
                               / sqrt(average((x-x.mean())**2)))

        features = []
        for p in pairs:
            a = block[:,p[0]]
            b = block[:,p[1]]
            # a = normalize(a)
            # b = normalize(b)
            a = abs(fft(a*w))[:block.shape[0]/2]
            b = abs(fft(b*w))[:block.shape[0]/2]
            c = log10(1+a*b)
            features.append(c)

        v = sum(features,axis=0)/len(features)

        return v-v.mean(); #normalize(v)

def fit_gaussian(x,y):
    """Provided the center parabola-like part of a Gaussian curve,
    returns a function that calculates any point on the curve."""
    p = polyfit(x,log(y),2)
    g = lambda x: exp(polyval(p,x))
    return g

def correlation_peaks(data, correlation_field, result_field):
    dat = data[correlation_field]
    res = []
    for d in dat:
        L = d.shape[0]
        g = fit_gaussian(arange(L/4,L*3/4), d[L/4:L*3/4])
        r = d-g(arange(L))
        xs = []
        ys = []
        for i in arange(r.shape[0]/2,r.shape[0]-3):
            if (r[i] > r[i+1] and r[i] > r[i+2]
                and r[i] >= r[i-1] and r[i] > r[i-2]):
                ys.append(r[i])
                xs.append(i)
            if (r[i] < r[i+1] and r[i] < r[i+2]
                and r[i] <= r[i-1] and r[i] < r[i-2]):
                ys.append(r[i])
                xs.append(i)
            if len(ys)==8:
                break
        for i in arange(r.shape[0]/2-1,4,-1):
            if (r[i] > r[i+1] and r[i] > r[i+2]
                and r[i] >= r[i-1] and r[i] > r[i-2]):
                ys.append(r[i])
                xs.append(i)
            if (r[i] < r[i+1] and r[i] < r[i+2]
                and r[i] <= r[i-1] and r[i] < r[i-2]):
                ys.append(r[i])
                xs.append(i)
            if len(ys)==16:
                break
        xs = xs[-1:7:-1] + xs[:8]
        dxs = array(xs[1:])-array(xs[:-1])
        res.append(dxs-average(dxs))
    data[result_field] = array(res)

def correlation_reduce(data, correlation_field, result_field):
    dat = data[correlation_field]
    res = []
    for d in dat:
        L = d.shape[0]
        g = fit_gaussian(arange(L/4,L*3/4), d[L/4:L*3/4])
        r = d-g(arange(L))
        v = []
        W = 64
        l = arange(W)
        for i in arange(r.shape[0]/W):
            v.append(polyfit(l,r[i*W:i*W+W],1)[:1])
        res.append(concatenate(v[len(v)*1/4:len(v)*3/4]))
    data[result_field] = array(res)

def correlation_reduce(data, correlation_field, result_field):
    dat = data[correlation_field]
    res = []
    for d in dat:
        f = abs(fft(d))
        f = f[:len(f)/2]
        sc = sum(f*arange(len(f)))/sum(f)
        slope = polyfit(arange(len(f)),f,1)[1]
        res.append([sc/100.0*2-1, slope/6*2-1])
    data[result_field] = array(res)
