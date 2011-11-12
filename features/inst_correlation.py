#!/usr/bin/env python

"""Implements unidirectional variant of the instantaneous covariance
and correlation filters described in Barbosa, Déchaine,
Vatikiotis-Bateson and Yehia, "Quantifying time-varying coordination
of multimodal speech signals using correlation map analysis." JASA,
2012."""

__all__ = ['inst_covariance', 'inst_correlation', 'inst_correlation_2d']

from pylab import *
from math import pi

# This is a 3rd-order fit to the eta/radial frequency relationship
# defined by "omega = arccos(1-((a-1)**2)/(2*a))"
wToEta=array([-0.01183542, -0.12620551,  1.07008204, -0.00857713])

def inst_covariance(w):
    """Generate the instantaneous covariance between two signals.
    `w' is frequency response in angular frequency."""
    eta = w*w*w*wToEta[0] + w*w*wToEta[1] + w*wToEta[2] + wToEta[3]
    if eta > 1.762:
        raise Exception('eta not defined for values > 1.762 (due to arccos)')
    a = exp(-eta)
    w = arccos(1-((a-1)**2)/(2*a))
    x, y = yield
    s = 0
    while True:
        r = x*y
        s = a*s+(1-a)*r
        x, y = yield s

def inst_correlation(w):
    """Generate the instantaneous correlation between two signals.
    `w' is frequency response in angular frequency."""
    cov1 = inst_covariance(w)
    cov1.next()
    cov2 = inst_covariance(w)
    cov2.next()
    cov3 = inst_covariance(w)
    cov3.next()
    cor = 0
    while True:
        x, y = yield cor
        cxy=cov1.send((x,y))
        cxx=cov2.send((x,x))
        cyy=cov3.send((y,y))
        s = sqrt(cxx*cyy)
        cor = (cxy/s if s!=0 else 0)

def inst_correlation_2d(w,delays):
    """Generate the correlation vector for a set of delays.  `w' is
    frequency response in angular frequency.  Delays are specified as
    a list of positive integers multiplying the sample period.  Output
    vectors can be concatenated to create a 2D correlation map."""
    cor0 = inst_correlation(w)
    cor0.next()
    corsx = [inst_correlation(w) for d in delays]
    corsy = [inst_correlation(w) for d in delays]
    [c.next() for c in corsx]
    [c.next() for c in corsy]
    cor = 0
    x, y = 0, 0
    m = max(delays)
    xs = zeros(m+1)
    ys = zeros(m+1)
    while True:
        xs[1:] = xs[:-1]
        ys[1:] = ys[:-1]
        xs[0], ys[0] = x, y
        cor = ( [ corsx[0].send((xs[m-d],ys[d])) for d in delays ] )
        x, y = yield cor

def gencos(phase,inc):
    while True:
        yield cos(phase)
        phase += inc
        if phase > 2*pi: phase -= 2*pi

def test_inst_1d():
    sr = 1000.0         # Sampling rate (Hz)
    freq = 50.0         # Frequency response (Hz)
    delay_s = 100*5/sr  # Delay (seconds)

    tm = arange(0,1+1/sr,1/sr)
    c1 = gencos(0,0.025)
    c2 = gencos(pi/2,0.025)
    cov = inst_covariance(freq/sr*pi)
    cov.next()
    cor = inst_correlation(freq/sr*pi)
    cor.next()
    cor2d = inst_correlation_2d(freq/sr*pi, arange(100)*5)
    cor2d.next()
    yc1 = zeros(len(tm))
    yc2 = zeros(len(tm))
    ycov = zeros(len(tm))
    ycor = zeros(len(tm))
    ycor2d = zeros((len(tm),100))
    for k,t in enumerate(tm):
        yc1[k] = c1.next()
        yc2[k] = c2.next()
        ycov[k] = cov.send((yc1[k],yc2[k]))
        ycor[k] = cor.send((yc1[k],yc2[k]))
        ycor2d[k] = cor2d.send((yc1[k],yc2[k]))
    clf()
    s=subplot(4,1,1)
    title('Test for 1D/2D inst. correlation, unidirectional, '
          +'%d Hz, sine/cosine'%(freq))
    plot(tm,yc1)
    plot(tm,yc2)
    ylabel('input')
    subplot(4,1,2)
    plot(tm,ycov)
    ylabel('covariance')
    subplot(4,1,3)
    plot(tm,ycor)
    ylabel('1d corr.')
    subplot(4,1,4)
    asp = (s.spines['left'].get_extents().height
           / s.spines['bottom'].get_extents().width)
    imshow(ycor2d.T, interpolation='nearest', cmap=cm.jet,
           origin='lower', extent=(tm[0], tm[-1], -delay_s/2, delay_s/2),
           aspect=(tm[-1]-tm[0])/delay_s*asp)
    ylabel('2d corr.')

if __name__=="__main__":
    figure(1)
    test_inst_1d()
    show()
