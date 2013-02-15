
import os.path
from numpy import array

here = os.path.dirname(__file__)

files = [#'motion-192.168.168.64-ipad.log',
         'motion-192.168.168.66-iphone.log',
         'motion-192.168.168.67-iphone.log']

def load_data():
    data = {}
    gestures = set()
    for fn in files:
        dat = {}
        for l in open(os.path.join(here,fn)):
            if l[:2] == 'G:':
                d = map(float,l[2:].split(','))
                g = int(l[2:].split(',')[1])
                if not dat.has_key(g): dat[g] = []
                dat[g].append(d[:1] + d[2:])
                gestures = gestures.union(set([g]))
        data[fn] = dat
    gestures = list(gestures)
    gestures.sort()
    return [[array(data[k][g]) for g in gestures[1:7]] for k in data]

def gesture_tags():
    return ['Circles',
            'Side to side',
            'Up and down',
            'Front and back',
            'Shaking',
            'Stop and go',
            'Nothing']
