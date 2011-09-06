#!/usr/bin/env python

__all__ = ['timeplot', 'matrixtimeplot']

from pylab import *

def timeplot(block, feature):
    data = block[feature]
    time = block['time']

    if len(data.shape)==1:
        plot(time, data)
    elif len(data.shape)==2:
        for i in xrange(data.shape[1]):
            subplot(data.shape[1],1,i+1)
            plot(time, data[:,i])

def matrixtimeplot(block, feature):
    data = block[feature]
    time = block['time']
    imshow(data.T, cmap='gray', interpolation='nearest',
           extent=[time[0], time[-1], 0, data.shape[1]],
           aspect=(time[-1]-time[0])/data.shape[1])
