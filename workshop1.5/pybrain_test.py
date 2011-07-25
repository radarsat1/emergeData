from pylab import array, plot, show, setp
from numpy import vdot, sqrt

from collections import defaultdict

from pybrain.datasets import *
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer

N_HIDDEN = 3
LEARNING_RATE = 0.01
LEARNING_RATE_DECAY = 1

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
    return sqrt(sum((x*x).transpose())) / 1000

#__all__ = ['read_tags', 'VideoTags']

def read_tags():
    """Read the tags associated with video frames in the file videotags.csv."""
    f = open('videotags.csv')
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
    
if __name__=='__main__':
    from pprint import pprint
    tags = read_tags()
    data, fields = read_minibees()
    
    # Create dataset
    print "Create dataset"
    ds = SupervisedDataSet(1, 1)
    #ds = ClassificationDataSet(1, class_labels = ["no jumping", "jumping"])
    individual = data[1] # for now we just load one person
    datapoints = []
    for point in individual:
        x = mag(point[5:8])
        if tags.frame_is(-1546120540, point[4], "jumping"):
          y = 1
        else:
          y = -1
        ds.addSample( (x), (y,) )
        datapoints.append([x, y])
    
    # Create network
    print "Build network"
    net = buildNetwork(1, N_HIDDEN, 1, bias=True, hiddenclass=TanhLayer)
    trainer = BackpropTrainer(net, ds, verbose = True)
    #, learningrate = LEARNING_RATE, lrdecay = LEARNING_RATE_DECAY, verbose = True)
    
    print "Train"
    print "Base error: " + str(trainer.testOnData())
    trainer.train();
    print "Final error: " + str(trainer.testOnData())
    
    activations = []
    for i in range(0, len(datapoints)):
#      print datapoints[i][0]
      out = net.activate( [ datapoints[i][0] ] )
      activations.append(out)
#    # Plot
    # Data
    setp(plot(individual[:,4], mag(individual[:,5:8])), color="black")
    
    # Correct classification (target)
    datapointsarray = array(datapoints)
    plot(individual[:,4], datapointsarray[:,1])
    
    # Classification (from NN)
    setp(plot(individual[:,4], activations), color="r")
    # Neural net classification
    show()
#
#  trnresult = percentError( trainer.testOnClassData(),
#                              trndata['class'] )
#    tstresult = percentError( trainer.testOnClassData(
#           dataset=tstdata ), tstdata['class'] )
#
#    print "epoch: %4d" % trainer.totalepochs, \
#          "  train error: %5.2f%%" % trnresult, \
#          "  test error: %5.2f%%" % tstresult