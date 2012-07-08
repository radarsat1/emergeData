#!/usr/bin/env python

__all__ = ["load_data"]

from pylab import *
from scipy.signal import lfilter
from scipy.interpolate import interp1d
from os import path
import bz2

sr = 100

def mag(x):
    """Calculate the magnitude of a 2D array of 1D vectors."""
    return sqrt((x*x).sum(1))

def plot_subject(n,s):
    g = zeros(11)
    for i in range(len(g)-1):
        g[i] = argmin(abs(1-(s[:,1]==(i+1))))
    g[-1] = s.shape[0]-1
    g = zip((g[:-1] + (g[1:]-g[:-1])/10).astype(int),
            (g[1:] - (g[1:]-g[:-1])/10).astype(int))

    subplot(1,1,n+1)
    plot(s[:,0], mag(s[:,2:5]))

    for c, n in zip("yrgmb"*4, arange(len(g))):
        fill_between([s[g[n][0],0], s[g[n][1],0]],
                     [ylim()[0]]*2, [ylim()[1]]*2,
                     color=c, alpha=0.3)

def crop_resample_subject(n,s):
    g = zeros(11)
    for i in range(len(g)-1):
        g[i] = argmin(abs(1-(s[:,1]==(i+1))))
    g[-1] = s.shape[0]-1
    gestidx = zip((g[:-1] + (g[1:]-g[:-1])/10).astype(int),
                  (g[1:] - (g[1:]-g[:-1])/10).astype(int))

    gestures = []
    for g in gestidx:
        time = arange(s[g[0],0]/1000.0, s[g[1],0]/1000.0-0.2, 0.01)
        x = interp1d(s[g[0]:g[1],0]/1000.0, s[g[0]:g[1],2])
        y = interp1d(s[g[0]:g[1],0]/1000.0, s[g[0]:g[1],3])
        z = interp1d(s[g[0]:g[1],0]/1000.0, s[g[0]:g[1],4])
        try:
            gestures.append(array([time, x(time), y(time), z(time)]).T)
        except:
            print s[g[0],0]-s[0,0], s[g[1],0]-s[0,0], min(time), max(time)
    return gestures

def load_data_raw():
    fn = path.join(path.dirname(__file__), 'motion_gestures_galaxytab.log.bz2')

    f = bz2.BZ2File(fn)
    data = []
    for l in f:
        if l[:2]=='G:':
            [time, gest, ax, ay, az] = l.split(':')[1].split(',')
            data.append([int(time),int(gest),float(ax),float(ay),float(az)])
    return [array(data)]

def load_data():
    data = load_data_raw()
    return [crop_resample_subject(n,s) for n,s in enumerate(data)]

def gesture_tags():
    return ['Button pushing',
            'Turning side to side',
            'Turning up and down',
            'Turning side to side with button pushing',
            'Turning up and down with button pushing',
            'Circles',
            'Circles with button pushing',
            'Beats',
            'Beats with button pushing',
            'Beats 2']

if __name__=='__main__':
    subject = load_data()

    figure(1).clf()
    [plot_subject(n,s) for n,s in enumerate(subject)]

    subject = [crop_resample_subject(n,s) for n,s in enumerate(subject)]

    figure(2)
    clf()
    for g in range(5):
        subplot(5,1,g+1)
        [plot(s[g][:,0], mag(s[g][:,1:4]), color='k', alpha=0.3) for s in subject]
        xlim(s[g][0,0], s[g][-1,0])

    show()
