#!/usr/bin/env python

from pylab import *
from scipy.signal import *
from scipy.interpolate import interp1d
from scikits.audiolab import Sndfile, Format
from read_minibees import read_minibees
import sys

def find_offsets(data):
    # Differentiate frame IDs.
    ids = data[:,3]
    idsWithDiff = array([lfilter([1,-1],[1],ids), ids]).T

    # Get index of each break
    indexes = [(n,x[1]) for n, x in enumerate(idsWithDiff)
               if x[0] > 0]

    # Find frame offsets for each index, i.e. the frame number of the
    # previous frame
    return [(i, (data[n-1,4], n)) for n, i in indexes]

def make_frame_offset_array(data, offsets):
    o = dict(offsets)
    return array([o.has_key(d[3]) and o[d[3]][0] or 0
                  for d in data])

def split_data_on_offsets(data, offsets):
    # Sort offsets by frame offset
    o = offsets[:]
    o.sort(key=lambda x: x[1])

    # For each offset, pull out the corresponding chunk of data
    d = []
    n = 0
    for i in o:
        k = i[1][1]
        d.append(data[n:k])
        n = k
    d.append(data[n:])

    # Replace the frames numbers of each
    of = dict(offsets)
    first = d[0][0,4]
    for i in d:
        i[:,4] += (of.has_key(i[0,3]) and of[i[0,3]][0] or 0) - first
    return d

def export_audio_vidId(fn, samplerate, vid, time, cols):
    f = [interp1d(time, cols[:,i]) for i in range(cols.shape[1])]
    fmt = Format(type=fn.split('.')[-1])

    newfn = '.'.join(fn.split('.')[:-2]
                     + [fn.split('.')[-2]+',%d'%vid]
                     + [fn.split('.')[-1]])

    print 'Writing',newfn
    wav = Sndfile(newfn, 'w', fmt, cols.shape[1], samplerate)
    a = arange(samplerate)/samplerate + time[0]
    for i in xrange(int((time[-1]-time[0]))):
        y = array([g(a+i) for g in f]).T
        wav.write_frames(y)
        print '%0.2f%%     \r'%(i / (time[-1]-time[0]) * 100),
        sys.stdout.flush()
    print '100%     '

def export_audio_all_minibees(minibees, prefix, ext):
    samplerate = 44100.0
    amplitude = 520.0

    for n in {10:minibees[10]}:
        data = minibees[n]
        offsets = find_offsets(data)
        d = split_data_on_offsets(data, offsets)

        newfn = '%s,%d.%s'%(prefix,n,ext)

        [export_audio_vidId(newfn, samplerate, a[0,3],
                            a[:,4]/30.0, a[:,5:8] / amplitude)
         for a in d]

if __name__=="__main__":
    minibees, fields = read_minibees()
    export_audio_all_minibees(minibees, 'minibee', 'aiff')
