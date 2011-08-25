
__all__ = ["load_data"]

from pylab import *
from scipy.signal import lfilter
from scipy.interpolate import interp1d
from os import path

sr = 100

def mag(x):
    """Calculate the magnitude of a 2D array of 1D vectors."""
    return sqrt((x*x).sum(1))

def fixtime_subject(n,s):
    t0 = s[0,0]

    dif = concatenate(([0],s[1:,2]-s[:-1,2]))

    time = (s[:,2] + lfilter([1],[1,-1],(dif < -2000)*1.0)*2560 - s[0,2]) / 100.0

    # first time of gesture 1
    t1 = time[argmin(abs(((s[:,6] > 0.5) - (s[:,6] < 1.5)*1)))]

    return array([time+t0-int(t0)-t1+26, s[:,3], s[:,4], s[:,5], s[:,6]]).T

def plot_subject(n,s):

    g = [0]*6
    g[1] = argmin(abs(((s[:,4] > 0.5) - (s[:,4] < 1.5)*1)))
    g[2] = argmin(abs(((s[:,4] > 1.5) - (s[:,4] < 2.5)*1)))
    g[3] = argmin(abs(((s[:,4] > 2.5) - (s[:,4] < 3.5)*1)))
    g[4] = argmin(abs(((s[:,4] > 3.5) - (s[:,4] < 4.5)*1)))
    g[5] = s.shape[0]-1

    subplot(6,1,n+1)
    plot(s[:,0], mag(s[:,1:4]))

    for c, n in zip("yrgmb", [0, 1, 2, 3, 4]):
        fill_between([s[g[n],0], s[g[n+1],0]],
                     [-100,-100], [600,600],
                     color=c, alpha=0.3)

    xlim(0, 110)

def crop_resample_subject(n,s):
    # Times of the gestures global across all subjects, from
    # observation after plotting.
    crop_times = [(8, 25),    # gesture 0
                  (27, 44.5), # gesture 1
                  (47, 63),   # gesture 2
                  (65, 83),   # gesture 3
                  (88, 102)]  # gesture 4

    gestures = []
    for t in crop_times:
        time = arange(t[0],t[1],0.01)
        t0 = argmin(abs(s[:,0] - t[0]))
        t1 = argmin(abs(s[:,0] - t[1]))+1
        while s[t0,0] > t[0]:
            t0 -= 1
        while s[t1,0] < t[1]:
            t1 += 1
            # print s[t0,0], s[t1,0], min(time), max(time)
        x = interp1d(s[t0:t1,0], s[t0:t1,1])
        y = interp1d(s[t0:t1,0], s[t0:t1,2])
        z = interp1d(s[t0:t1,0], s[t0:t1,3])
        try:
            gestures.append(array([time, x(time), y(time), z(time)]).T)
        except:
            print s[t0,0], s[t1,0], min(time), max(time)
    return gestures

def load_data():
    fn = path.join(path.dirname(__file__), 'gestures_idmil_230811.csv.bz2')
    data = loadtxt(fn, delimiter=',', skiprows=1)
    subject = [array([d[0:7] for d in data if d[7]==(s+1)]) for s in range(6)]
    subject = [fixtime_subject(n,s) for n,s in enumerate(subject)]
    subject = [crop_resample_subject(n,s) for n,s in enumerate(subject)]
    return subject

if __name__=='__main__':
    data = loadtxt('../data/gestures_idmil_230811.csv.bz2', delimiter=',', skiprows=1)
    subject = [array([d[0:7] for d in data if d[7]==(s+1)]) for s in range(6)]
    subject = [fixtime_subject(n,s) for n,s in enumerate(subject)]

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
