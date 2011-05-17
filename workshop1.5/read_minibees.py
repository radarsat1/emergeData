#!/usr/bin/env python

from pylab import array, plot, show
from numpy import vdot, sqrt

def ntp2sec(sec, frac):
    return sec + frac/float(1<<32)

def readints(f, N=None):
    """Read rows of comma-separated integers into a 2D numpy array."""
    a = [[] for i in range(11)]
    for n, i in enumerate(f):
        b = map(int,i.split(','))
        a[b[4]].append(b[:2]+[ntp2sec(b[0],b[1])]+b[2:4]+b[5:])
        if N!=None and n >= N:
            break
    return (dict([(n, array(i)) for n, i in enumerate(a) if i!=[]]),
            ('sec','frac','ntpsec','video','frame','accelx','accely','accelz'))

def read_minibees(N=None):
    """Read the data from workshop1.5 (aka Session 2) from a bzipped file."""
    from bz2 import BZ2File
    return readints(BZ2File("session2_minibees_cropped.csv.bz2"), N)

def mag(x):
    """Calculate the magnitude of a 2D array of 1D vectors."""
    return sqrt(sum((x*x).transpose()))

if __name__=="__main__":
    a, fields = read_minibees(5000)
    for x in a:
        plot(a[x][:,4], mag(a[x][:,5:8]))
    show()
