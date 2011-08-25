#!/usr/bin/env python

from minibee import Minibees
import sys, serial, time, collections
from pylab import *

if len(sys.argv) > 1:
    ser = serial.Serial(sys.argv[1])
else:
    ser = serial.Serial('/dev/ttyUSB0')
ser.baudrate = 19200

data = collections.defaultdict(lambda: [])
count = collections.defaultdict(lambda: 0)
missed = collections.defaultdict(lambda: 0)
total = collections.defaultdict(lambda: 0)
msgids = collections.defaultdict(lambda: None)
accum_perc_missed = []

t = time.time()
start_time = t
def with_data(nodeid, msgid, d):
    global t
    data[nodeid].append([msgid] + d)
    count[nodeid] += 1
    total[nodeid] += 1
    if msgids[nodeid]==None:
        msgids[nodeid] = msgid
    else:
        m = msgids[nodeid] + 1
        if m - msgid > 256/2:
            m -= 256
        while m < msgid:
            m += 1
            missed[nodeid] += 1
            total[nodeid] += 1
        msgids[nodeid] = m

    perc_missed = [(missed[x]*100 / float(total[x]))
                   for x in missed.keys()]
    if len(perc_missed)>0:
        perc_missed = sum(perc_missed)/float(len(perc_missed))
    else:
        perc_missed = 0

    accum_perc_missed.append(perc_missed)

    if time.time() > t+2:
        t = time.time()
        data[nodeid] = []
        print 'num_nodes: %d, percent_missed: %0.2f%%'%(len(data),perc_missed)

    if t > (start_time + 300):
        plot(accum_perc_missed)
        print average(accum_perc_missed[:-len(accum_perc_missed)/4])
        show()

Minibees(ser, with_data, msg_period=100, samps_per_msg=10).run()


# results
# 25, 1, ~23%      40 Hz
# 50, 1, ~10%      20 Hz
# 100, 1, ~6%      10 Hz
# 200 (unable to use)
# 300, 1, ~2.5%    3 Hz

# 50, 2, ~11%      40 Hz
# 100, 2, ~6%      20 Hz
# 300, 2, ~2%      6.7 Hz

# 100, 10, ~20%    100 Hz

# 300, 10, ~3%     33 Hz
# 300, 14, ~4.5%   46 Hz

# Packet loss seems to be fairly linear and predictable
# Better throughput with lower rate, more samples per message.
# Could interleave samples to lessen impact of missed packets.
# Could increase baud rate.
# Could use hand-shaking/retry for confirmation messages.
# Tests performed with only 6 minibees.
