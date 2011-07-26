from pylab import array, plot, show, setp
from numpy import vdot, sqrt
from collections import defaultdict

__all__ = ['read_minibees', 'read_tags', 'VideoTags']

# Data reading functions
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

def read_minibees(N=None,filename="session2_minibees_cropped.csv.bz2"):
    """Read the data from workshop1.5 (aka Session 2) from a bzipped file."""
    from bz2 import BZ2File
    return readints(BZ2File(filename), N)
    

# Tags reading functions
def read_tags(filename='videotags.csv'):
    """Read the tags associated with video frames in the file videotags.csv."""
    f = open(filename)
    skip = f.readline()
    tags = defaultdict(lambda: [])
    for line in f:
        fields = line.rstrip().split(',')
        vid = int(fields[0])
        framestart = int(fields[1])
        frameend = None if len(fields[2])==0 else int(fields[2])
        frametags = set(fields[3:])
        tags[vid].append((framestart, frameend, frametags))
    return VideoTags(dict(tags))

class VideoTags(object):
    def __init__(self, tags):
        self.tags = tags

    def frame_tags(self, vid, frame):
        """Find all tags associated with a given video frame."""
        if not self.tags.has_key(vid):
            raise Exception("Video ID not found.")
        v = self.tags[vid]
        L = []
        for interval in v:
            if frame >= interval[0] and frame <= interval[1]:
                L += interval[2]
        return set(L)

    @property
    def videos(self):
        return self.tags.keys()

    @property
    def all_tags(self):
        """The set of all tags as a sorted list."""
        t = list(set.union(*[L[2] for v in self.tags.values() for L in v]))
        t.sort()
        return t
        
    def frame_is(self, vid, frame, tag):
      return (tag in self.frame_tags(vid, frame))
      
# Data + tags reading functions
def read_minibees(N=None,filename="session2_minibees_cropped.csv.bz2"):
    """Read the data from workshop1.5 (aka Session 2) from a bzipped file."""
    from bz2 import BZ2File
    return readints(BZ2File(filename), N)
