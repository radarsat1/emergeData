from pylab import *
from numpy import vdot, sqrt

from collections import defaultdict, deque
from minibees_common import *
from pprint import pprint

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import sys

class WindowedStats(object):
    def __init__(self, windowSize):
        self.windowSize = windowSize
        self.buffer = deque([])
    
    def add(self, x):
      self.buffer.append(x)
      if (len(self.buffer) > windowSize):
        self.buffer.popleft()
      
    def getStats(self):
      x = self.buffer[0]
      minVal = x
      maxVal = x
      mean   = x
      for i in range(1, len(self.buffer)):
        x = self.buffer[i]
        minVal = min(x, minVal)
        maxVal = max(x, maxVal)
        mean   += x
      mean /= len(self.buffer)
      return [ mean, minVal, maxVal ]      

def mag(x):
    """Calculate the magnitude of a 2D array of 1D vectors."""
    return sqrt(sum((x*x).transpose()))

if __name__=='__main__':
    tags = read_tags()
    data, fields = read_minibees()
    
    if (len(sys.argv) != 4):
      print "Usage: " + sys.argv[0] + " <uid> <tagname> <windowsize>"
      exit(0)
    
    uid = int(sys.argv[1])
    tag = sys.argv[2]
    windowSize = int(sys.argv[3])
    
    videoId = -1546120540
    
    tagged = []
    notTagged = []
    
    individual = data[uid]
    stats = WindowedStats(windowSize)
    
    for point in individual:
      if (int(point[3]) != videoId):
        continue
      stats.add( mag(point[5:8]) )
      x = stats.getStats()
      if tags.frame_is(videoId, point[4], tag):
        tagged.append([point[4]] + x)
      else:
        notTagged.append([point[4]] + x)
        
    fig = plt.figure()
    #ax = Axes3D(fig)
    ax = fig.add_subplot(111, projection='3d')
    if (tagged != []):
      tagged = array(tagged)
      ax.scatter(tagged[:,1], tagged[:,2], tagged[:,3], color="blue", marker='d')
    if (notTagged != []):
      notTagged = array(notTagged)
      ax.scatter(notTagged[:,1], notTagged[:,2], notTagged[:,3], color="red", marker='x')
    plt.title("Tag \"" + tag + "\" for individual #" + str(uid))
    ax.set_xlabel("mean")
    ax.set_ylabel("min")
    ax.set_zlabel("max")
    
    tr = Rectangle((0, 0), 1, 1, fc="b")
    ntr = Rectangle((0, 0), 1, 1, fc="r")
    plt.legend([tr, ntr], [tag, "not " + tag], loc="lower left")
    #plt.legend( (taggedPlot, notTaggedPlot), (tag, "not "+tag), loc="upper center")
    plt.savefig("plots/plot_tag--mag-mean-min-max--" + tag + "_" + str(windowSize) + "_" + str(uid) + ".png")
#    plt.show()