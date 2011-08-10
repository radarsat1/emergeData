#!/usr/bin/env python

from pylab import *
from read_minibees import read_minibees, mag
from read_tags import read_tags
import scipy.optimize as opt
import scipy.signal as sig
from scipy.interpolate import interp1d

# def load_gestures():
#     from bz2 import BZ2File
#     gestures = []
#     #for g in BZ2File('../../dotminibee/software/gestures.txt.bz2'):
#     for g in BZ2File('gestures.txt.bz2'):
#         d = [float(x) for x in g.split('[')[1].split(']')[0].split(',')]
#         gestures.append(d)
#     return array(gestures)

# data, sr = mag(load_gestures()), 200.0
# fulldata = data
# data = sig.lfilter(*sig.butter(2, 0.1, 'low'),x=fulldata)[::10]
# sr = 200/10

minibees, fields = read_minibees()

def unwrap_time(time, timediff):
    brks = [n for n,d in enumerate((time[1:]-time[:-1])) if d < -timediff]
    idx = arange(time.size)
    return sum([time] + [(idx > b)*time[b] for b in brks], axis=0)

time_range = (0,100000000000)
all_interp = {}
for m in minibees.keys():
    time = unwrap_time(minibees[m][:,4]/30.0, 500)
    time_range = (max(time_range[0], time[0]),
                  min(time_range[1], time[-1]))

for m in minibees.keys():
    time = unwrap_time(minibees[m][:,4]/30.0, 500)
    all_interp[m] = interp1d(time, mag(minibees[m][:,5:8]))

subsamp = 3
time = arange((time_range[1]-time_range[0])*subsamp)/subsamp+time_range[0]
hopsize = 20
length = 100
hopidx = arange(time.size)[:-length:hopsize]
hoptime = array([time[i] for i in hopidx])
all_mag = array([all_interp[m](time) for m in sort(minibees.keys())])

ccorr = [sum(corrcoef(all_mag[:,i:i+length])) for i in hopidx]
ccov = [sum(cov(all_mag[:,i:i+length])) for i in hopidx]

rc('legend',fontsize=8)

clf()
subplot(3,1,1)
plot(hoptime, ccorr, label='correlation')
legend()
subplot(3,1,2)
plot(hoptime, ccov, label='covariance')
legend()
subplot(3,1,3)
[plot(time, all_mag[m,:], alpha=0.1) for m in range(all_mag.shape[0])]

from itertools import combinations, chain
def powerset2(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(2,len(s)+1))

figure(1)
clf()
groups = powerset2(arange(len(minibees)))
c = cov(all_mag[:,1000:1200])
s = subplot(1,1,1)
for n, g in enumerate(groups):
    pairs = combinations(g, 2)
    a = average([c[p[0],p[1]] for p in pairs])        
    plot(n, a, 'bo')
    if a > 9000:
        s.text(n+1, a+100, str([minibees.keys()[m] for m in g]))
suptitle('Avg. covariance between groups of minibees at time %.2f-%.2f.'%(time[1000],time[1200]))

figure(2)
clf()
groups = powerset2(arange(len(minibees)))
c = cov(all_mag)
s = subplot(1,1,1)
avgs = []
for n, g in enumerate(groups):
    pairs = combinations(g, 2)
    a = average([c[p[0],p[1]] for p in pairs])        
    avgs.append(a)
    plot(n, a, 'bo')
    if a > 5000:
        s.text(n+1, a+100, str([minibees.keys()[m] for m in g]))
suptitle('Avg. covariance between groups of minibees, whole time.')
        
#figure(2)
#imshow(c, interpolation='nearest', cmap='gray')
