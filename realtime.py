#!/usr/bin/env python

from pylab import *
from data import gestures_idmil_230811
import operations.display
import operations.classifier
import features.basic
import features.blockbased

def stream_block_processor(t,a):
    """Break up an incoming stream into 1024-sized blocks. Add 16
    extra samples to make the block-based analysis pull out a single
    block properly."""
    times = zeros(1024+16)
    accels = zeros((1024+16,3))
    pos = 0
    while True:
        times[pos] = t
        accels[pos] = a
        pos += 1
        if pos >= (1024+16):
            d = {'time':times, 'accel':accels}
            features.basic.magnitude(d)
            features.basic.hipassed(d,2,0.2)
            cor1 = features.blockbased.windowed(d, 'mag',
                                                features.blockbased.autocorrelation,
                                                'autocorrelation',
                                                size=1024, hopsize=16)
            cor2 = features.blockbased.windowed(d, 'hipassed',
                                                features.blockbased.axes_correlation,
                                                'axes_correlation',
                                                size=1024, hopsize=16)
            cor2['autocorrelation'] = cor1['autocorrelation']
            times[:1024] = times[-1024:]
            accels[:1024] = accels[-1024:]
            pos = 1024
            t, a = yield cor2
        else:
            t, a = yield None

def run(data,s):
    time = concatenate([data[s][g][:,0] for g in range(5)])
    accel = concatenate([data[s][g][:,1:] for g in range(5)])
    proc = stream_block_processor(time[0],accel[0,:])
    proc.next()
    print len(time)
    res = []
    for i,_ in enumerate(time[1:]):
        cor = proc.send((time[i+1],accel[i+1,:]))
        if cor != None:
            res.append(cor)
    print len(res)

data = gestures_idmil_230811.load_data()
run(data,0)
