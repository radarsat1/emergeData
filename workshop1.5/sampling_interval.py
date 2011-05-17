#!/usr/bin/env python

from pylab import plot, show, figure
from numpy import zeros, ones, concatenate

from read_minibees import read_minibees

if __name__=="__main__":
    a, fields = read_minibees()
    b = a[2]

    # Adjust the frame count by an offset, determined by manually
    # looking in the the data to see where it indicates no new frame
    # numbers were received (stopframe), and when it again begins to
    # receive (restartframe).  The id of the take number is a[n][:,3].
    # Frame count is a[n][:,4].

    stopframe = 3680
    restartframe = 3764
    frameoffset = concatenate((zeros(restartframe),
                              ones(len(b)-restartframe)*b[stopframe,4]))

    frames = (b[:,4] + frameoffset - b[0,4]) / 30.0
    times = b[:,2] - b[0,2]

    figure(1)
    plot(frames, frames)
    plot(frames, frames, 'o')
    plot(times, times)
    plot(times, times, 'o')

    figure(2)
    plot(times[1:] - times[:-1])
    plot(frames[1:] - frames[:-1])
    show()
