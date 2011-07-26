from pylab import *
from numpy import vdot, sqrt

from collections import defaultdict
from minibees_common import *
from pprint import pprint

import sys

def mag(x):
    """Calculate the magnitude of a 2D array of 1D vectors."""
    return sqrt(sum((x*x).transpose()))

if __name__=='__main__':
    tags = read_tags()
    data, fields = read_minibees()
    
    if (len(sys.argv) != 3):
      print "Usage: " + sys.argv[0] + " <uid> <tagname>"
      exit(0)
    
    uid = int(sys.argv[1])
    tag = sys.argv[2]
    videoId = -1546120540
    
    tagged = []
    notTagged = []
    
    individual = data[uid]
    for point in individual:
      if (point[3] != videoId):
        continue
      x = mag(point[5:8])
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
    title("Tag \"" + tag + "\" for individual #" + str(uid))
    xlabel("frame")
    ylabel("magnitude")
    legend(loc="upper center")
    savefig("plots/plot_tag--mag--" + tag + "_" + str(uid) + ".png")
    #show()