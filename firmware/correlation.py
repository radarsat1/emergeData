#!/usr/bin/env python

from pylab import *
from math import pi

# This is a 3rd-order fit to the eta/radial frequency relationship
# defined by "omega = arccos(1-((a-1)**2)/(2*a))"
wToEta=array([-0.01183542, -0.12620551,  1.07008204, -0.00857713])

def inst_covariance(w):
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
        cor = cxy/sqrt(cxx*cyy)

def gencos(phase,inc):
    while True:
        yield cos(phase)
        phase += inc
        if phase > 2*pi: phase -= 2*pi

def run():
    sr = 1000.0
    tm = arange(0,1,1/sr)
    c1 = gencos(0,0.025)
    c2 = gencos(pi/2,0.025)
    cov = inst_covariance(50/sr*pi)
    cov.next()
    cor = inst_correlation(50/sr*pi)
    cor.next()
    yc1 = zeros(len(tm))
    yc2 = zeros(len(tm))
    ycov = zeros(len(tm))
    ycor = zeros(len(tm))
    for k,t in enumerate(tm):
        yc1[k] = c1.next()
        yc2[k] = c2.next()
        ycov[k] = cov.send((yc1[k],yc2[k]))
        ycor[k] = cor.send((yc1[k],yc2[k]))
    clf()
    subplot(3,1,1)
    plot(tm,yc1)
    plot(tm,yc2)
    subplot(3,1,2)
    plot(tm,ycov)
    subplot(3,1,3)
    plot(tm,ycor)
    show()
run()
