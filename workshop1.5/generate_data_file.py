#!/usr/bin/env python2.6

import os
import numpy
from tempfile import mkstemp
from string import join

from inspect import *

from pylab import *

from minibees_common import *
from filtering import *

from progressbar import ProgressBar

    
def generate_data_file(filename, columns):
  videoId = -1546120540
  
  tags = read_tags()
  data, fields = read_minibees()
  outputData = []
  
  columnNames = [ "uid", "frame" ]
  for t in tags.all_tags:
    columnNames.append(t)
  for func in columns:
    columnNames += func.name()
  for i, val in enumerate(columnNames):
    columnNames[i] = str(i) + "_" + val
  
  n = len(data)
  pbar = ProgressBar(0, n, mode='static')
  print "Reading/loading data"
  pbar.update()
  for uid in data:
    for func in columns:
      func.reset()
    individual = data[uid]
    for point in individual:
      if (point[3] != videoId):
        continue
      
      frame = point[4]

      row = []
      
      row.append(uid)     # user id
      row.append(frame)   # frame number
      
      currentTags = tags.frame_tags(videoId, frame)
      for t in tags.all_tags:
        if (t in currentTags):
          row.append(1)
        else:
          row.append(0)
      
      x = point[5:8]         # get xyz-acceleration
      
      # Append all functions (filters)
      for func in columns:
#        if (isclass(func)):
        val = func.call(x)
#        else:
#          val = func(x)
        row += val
      
      outputData.append(row)
    
    pbar.increment()
  
  pbar.finish()
#  print outputData
  
  print "Saving..."
  basename, extension = os.path.splitext(filename)
  # TODO: support for gzip
  if (extension == "npy"):
    print "NPY format not supported yet, saving to text file"
  #  outputData = array(outputData)
  #  numpy.save(filename, outputData, fmt="%f")
  f = open(filename, "w")
  f.write("# " + join(columnNames) + "\n")
  for row in outputData:
    for col in row:
      f.write(str(col) + " ")
    f.write("\n")
  f.close()
  print "Done."

if __name__=='__main__':
  if (len(sys.argv) != 2):
    print "Usage: " + sys.argv[0] + " <filename>"
    exit(0)
  
  filename = sys.argv[1]
  
  generate_data_file(filename, [ RMS(), Accel(), Jerk(), BasicStats(10), BasicStats(100) ])
  