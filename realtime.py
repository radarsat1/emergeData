#!/usr/bin/env python

from pylab import *
from data import gestures_idmil_230811
import operations.display
import operations.classifier
import features.basic
import features.blockbased
from minibee import Minibee
import serial

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
            cor = features.blockbased.windowed(d, 'hipassed',
                                               features.blockbased.axes_correlation,
                                               'axes_correlation',
                                               size=1024, hopsize=16)
            features.blockbased.correlation_reduce(cor, 'axes_correlation',
                                                   'axes_correlation_reduced')
            times[:1024] = times[-1024:]
            accels[:1024] = accels[-1024:]
            pos = 1024
            # Throw out everything but the reduced data
            t, a = yield {'axes_correlation_reduced':
                              cor['axes_correlation_reduced'],
                          'time': cor['time']}
        else:
            t, a = yield None

def labdata_run():
    data = gestures_idmil_230811.load_data()
    suj = 0
    time = concatenate([data[suj][g][:,0] for g in range(5)])
    accel = concatenate([data[suj][g][:,1:] for g in range(5)])
    proc = stream_block_processor(time[0],accel[0,:])
    proc.next()
    print len(time)
    res = []
    for i,_ in enumerate(time[1:]):
        cor = proc.send((time[i+1],accel[i+1,:]))
        if cor != None:
            res.append(cor)
    print len(res)

def online_accel_processor():
    t,a = yield None
    proc = stream_block_processor(t,a)
    proc.next()
    cor = proc.send((t,a))
    while True:
        t,a = yield cor
        cor = proc.send((t,a))

def test_minibee():
    if len(sys.argv) > 1:
        ser = serial.Serial(sys.argv[1])
    else:
        ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 19200

    ion()

    proc = online_accel_processor()
    proc.next()
    this_nodeid = 1
    t = [0]
    time = []
    tcors = []
    def minibee_cb(nodeid, msgid, d):
        if nodeid != this_nodeid:
            print 'Unknown node',nodeid
            return
        # TODO: handle time using msgid
        t[0] += 1
        cor = proc.send((t[0], d))
        if cor!=None:
            time.append(t[0])
            tcors.append(cor['axes_correlation_reduced'][0])
            clf()
            plot(time, [c[0] for c in tcors])
            plot(time, [c[1] for c in tcors])
            draw()
    Minibee(ser, minibee_cb,
            msg_period=100, samps_per_msg=10).run()

if __name__=='__main__':
    test_minibee()

    # labdata_run()
