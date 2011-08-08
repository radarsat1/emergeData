from pylab import *
from collections import deque
from minibees_common import Statistics

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

class BasicStats(Filtering):
    def __init__(self, windowSize):
      self.stats = Statistics(windowSize)
    
    def reset(self):
      self.stats.reset()
    
    def call(self, v):
      self.stats.add(mag(v))
      return self.stats.getStats()
      
    def name(self):
      return map( lambda x: x + "_" + str(self.stats.windowSize), ['mean', 'stddev', 'min', 'max'])
