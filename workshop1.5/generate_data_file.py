import os
import numpy
from tempfile import mkstemp
from string import join

from collections import deque

from inspect import *

from pylab import *

from minibees_common import *
from progressbar import ProgressBar

def mag(v):
  return sqrt(sum((v*v).transpose()))
  
class Filtering:
  def reset(self):
    return
  
  def call(self, v):
    return v.tolist()

  def name(self):
    return None

class RMS(Filtering):
  def call(self, v):
    return [mag(v)]
    
  def name(self):
    return ["rms"]

class Accel(Filtering):
  def call(self, v):
    return v.tolist()
    
  def name(self):
    return ["ax", "ay", "az"]

class Jerk(Filtering):
  def reset(self):
    self.prev = array([0, 0, 0])
  
  def call(self, v):
    # TODO: adjust given frame
    dv = v - self.prev
    self.prev = v
    jrms = mag(dv)
    dv = dv.tolist()
    dv.append(jrms)
    return dv
    
  def name(self):
    return ["jx", "jy", "jz", "jrms"]

class MeanMinMax(Filtering):
    def __init__(self, windowSize):
      self.windowSize = windowSize
      self.buffer = deque([])
    
    def reset(self):
      self.buffer = deque([])
    
    def call(self, v):
      self.add(mag(v))
      return self.getStats()
      
    def name(self):
      return [ "mean_" + str(self.windowSize), "min_" + str(self.windowSize), "max_" + str(self.windowSize) ]
    
    def add(self, v):
      self.buffer.append(v)
      if (len(self.buffer) > self.windowSize):
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
    outputData = array(outputData)
    numpy.save(filename, outputData, fmt="%f")
  else:
    f = open(filename, "w")
    f.write("# " + join(columnNames) + "\n")
    for row in outputData:
      for col in row:
        f.write(str(col) + " ")
      f.write("\n")
    f.close()
#    tmpfile = mkstemp('','tmp_', '/tmp')
#    tmpfile = tmpfile[1]
#    numpy.savetxt(tmpfile, outputData)
#    os.system('echo "# ' + join(columnNames) + ' > ' + filename)
#    os.system('cat ' + tmpfile + ' >> ' + filename)
#    os.remove(tmpfile)
  print "Done."
#  numpy.save("/tmp/out.npy", outputData)

if __name__=='__main__':
  if (len(sys.argv) != 2):
    print "Usage: " + sys.argv[0] + " <filename>"
    exit(0)
  
  filename = sys.argv[1]
  
  generate_data_file(filename, [ RMS(), Accel(), Jerk(), MeanMinMax(100) ])
  