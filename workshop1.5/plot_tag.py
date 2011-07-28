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
    if (len(sys.argv) != 3):
      print "Usage: " + sys.argv[0] + " <uid> <tagname>"
      exit(0)
    
    if (sys.argv[1] == "all"):
      uids = [1,2,3,5,7,8,9,10]
    else:
      uids = sys.argv[1].split(",")
    tag = sys.argv[2]

    videoId = -1546120540
    
    tags = read_tags()
    data, fields = read_minibees()
    
    tagged = []
    notTagged = []
    
    for uid in uids:
      uid = int(uid)
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
    title("Tag \"" + tag + "\" for individuals " + sys.argv[1])
    xlabel("frame")
    ylabel("magnitude")
    legend(loc="upper center")
    savefig("plots/plot_tag--mag--" + tag + "_" + sys.argv[1].replace(",","-") + ".png")
    #show()