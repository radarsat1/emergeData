from pylab import *
from numpy import vdot, sqrt

from collections import defaultdict, deque
from minibees_common import *
from pprint import pprint

import sys

class WindowedXYZ(object):
    def __init__(self, windowSize):
        self.windowSize = windowSize
        self.buffer = deque([])
    
    def reset(self):
      self.buffer = deque([])
    
    def add(self, x):
      self.buffer.append(x)
      if (len(self.buffer) > windowSize):
        self.buffer.popleft()
      
    def getMean(self):
#      print "---"
      mean = array([0, 0, 0])
      for i in range(0, len(self.buffer)):
#        print "+ " + str(self.buffer[i])
        mean += self.buffer[i]
#        print "= " + str(mean)
      mean /= len(self.buffer)
#      print "mean: " + str(mean)
      return mean

def mag(x):
    """Calculate the magnitude of a 2D array of 1D vectors."""
    return sqrt(sum((x*x).transpose()))

if __name__=='__main__':
    if (len(sys.argv) != 4):
      print "Usage: " + sys.argv[0] + " <uid> <tagname> <windowsize>"
      exit(0)
    
    if (sys.argv[1] == "all"):
      uids = [1,2,3,5,7,8,9,10]
    else:
      uids = sys.argv[1].split(",")
    tag = sys.argv[2]
    windowSize = int(sys.argv[3])

    videoId = -1546120540
    
    tags = read_tags()
    data, fields = read_minibees()
    
    tagged = []
    notTagged = []
    window = WindowedXYZ(windowSize)
    
    for uid in uids:
      uid = int(uid)
      individual = data[uid]
      window.reset()
      for point in individual:
        if (point[3] != videoId):
          continue
        window.add( point[5:8] )
        x = mag( window.getMean() )
        if tags.frame_is(videoId, point[4], tag):
          tagged.append([point[4], x])
        else:
          notTagged.append([point[4], x])
    
    clf()
    if (tagged != []):
      tagged = array(tagged)
      plot(tagged[:,0], tagged[:,1], "b.", label=tag)
    if (notTagged != []):
      notTagged = array(notTagged)
      plot(notTagged[:,0], notTagged[:,1], "r.", label="not " + tag)
    title("Tag \"" + tag + "\" (window=" + str(windowSize) + ", id=" + sys.argv[1] + ")")
    xlabel("frame")
    ylabel("magnitude")
    legend(loc="upper center")
    savefig("plots/plot_tag--mag-add--" + tag + "_" + str(windowSize) + "_" + sys.argv[1].replace(",","-") + ".png")
    #show()