#!/usr/bin/env python2.6

from pylab import *
from progressbar import ProgressBar
import matplotlib.pyplot as plt
import numpy
from collections import defaultdict
from string import join

from minibees_common import *

def afilter(function, arr):
  return array(filter(function, arr.tolist()))

def generate_plot_from_array(data, columnNames, xcol, ycol, **kwargs):
  # TODO support for 3d
  #zcol = kwargs.get("zcol", None)
  # TODO automatic finding of labels from head comment # (won't work with .npy files)
  #xlabel = kwargs.get("xlabel", labels[xcol])
  #ylabel = kwargs.get("ylabel", labels[ycol])
  if (isinstance(xcol, str)):
    xcolName = xcol
    xcol = columnNames.index(xcolName)
  if (isinstance(ycol, str)):
    ycolName = ycol
#    print "YCOLNAME: " + ycolName
#    print "COUMN: " + columnNames
    ycol = columnNames.index(ycolName)
  
  xlabel = kwargs.get("xlabel", xcolName)
  ylabel = kwargs.get("ylabel", ycolName)
  title  = kwargs.get("title",  "Plot of " + ylabel + " given " + xlabel)
  alpha  = kwargs.get("alpha", 0.5)
  noother = kwargs.get("noother", False)
  
  uids   = kwargs.get("uids", "all")
  allUids = False
  if (uids == "all"):
    uids = [1,2,3,5,7,8,9,10]
  #  allUids = True
  elif (isinstance(uids, str)):
    uids = uids.split(",")
  elif (isinstance(uids, int)):
    uids = [uids]
    
  # Filter out uids
  if (not allUids):
    data = afilter( lambda x : x[0] in uids, data )

  # Create different arrays for the different tags
  tags   = kwargs.get("tags", "jumping")  
  if (isinstance(tags, str)):
    tags = [ tags ]
  allTags = read_tags().all_tags
  tagsIdx = defaultdict(lambda: [])
  for i, t in enumerate(tags):
    for j, tt in enumerate(allTags):
      if t == tt:
        tagsIdx[t] = 2+int(j)

  taggedData = defaultdict(lambda: [])
  for i, row in enumerate(data.tolist()):
    noTags = True
    for t in tagsIdx:
      idx = tagsIdx[t]
      if (row[idx] == 1):
        taggedData[t].append(row)
        noTags = False
    if noTags:
      taggedData['other'].append(row)
  
 # print taggedData
  plt.clf()
  plt.title(title)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  # TODO: plot different tags + autres (no tag)
  for t in taggedData:
    if (t == 'other'): # stupid HACK to put "others" always at the end
      continue
    d = array(taggedData[t])
    plt.plot(d[:,xcol], d[:,ycol], '.', alpha=alpha, label=t)
  if (not noother):
    d = array(taggedData['other'])
    plt.plot(d[:,xcol], d[:,ycol], '.', alpha=alpha, label='other')
  plt.legend(loc="lower center")
  #plt.show()
    
  outputfile = "plots/plot--" + xlabel.replace(" ", "_") + "-" + ylabel.replace(" ", "_") + "--";
  if (kwargs.get("uids", "all") == "all"):
    outputfile += "all"
  else:
    outputfile += join(uids, ",")
  outputfile += "--" + join(tags, '_')
  if (noother):
    outputfile += "_no-other"
  outputfile += ".png"
  print "Saving plot to file " + outputfile               
  plt.savefig(outputfile)
  print "done."

def load_column_names(filename):
  f = open(filename, "r")
  columnNames = f.readline().replace("# ", "").replace("\n", "").split(" ")
#  print "BEF"
#  print columnNames
  columnNames = map ( lambda x: x.split('_', 1)[1], columnNames)
#  print "AFT"
#  print columnNames
  f.close()
  return columnNames

def load_data(filename):
  return numpy.loadtxt(filename)

def generate_plot_from_file(filename, xcol, ycol, **kwargs):
  data = load_data(filename)
  columnNames = load_column_names(filename)
  generate_plot_from_array(data, columnNames, xcol, ycol, **kwargs)

if __name__=='__main__':
  if (len(sys.argv) != 2):
    print "Usage: " + sys.argv[0] + " <filename>"
    exit(0)
  
  filename = sys.argv[1]
  
  generate_plot_from_file(filename, "max_10", "max_100", uids="all", tags=["standing", "jumping", "fistpump"], alpha=0.3, noother=True)
  #generate_plot_from_file(filename, 1, 22, uids="all", tags=["jumping", "fistpump"], xlabel="frame", ylabel="magnitude")
#  generate_plot_from_file(filename, 23, 24, uids="all", tags=["standing", "fistpump"], xlabel="ax", ylabel="ay", alpha=0.5, noother=True)
#  generate_plot_from_file(filename, 1, 22, uids="all", tags=["standing", "fistpump"], xlabel="frame", ylabel="magnitude", alpha=0.5, noother=True)
#  generate_plot_from_file(filename, "frame", "mean_10", uids="all", tags=["standing", "jumping", "fistpump"], alpha=0.5, noother=True)
#  generate_plot_from_file(filename, "mean_10", "mean_100", uids="all", tags=["standing", "jumping", "fistpump"], alpha=0.3, noother=True)
#  generate_plot_from_file(filename, "stddev_10", "stddev_100", uids="all", tags=["standing", "jumping", "fistpump"], alpha=0.3, noother=True)
#  generate_plot_from_file(filename, "mean_100", "stddev_100", uids="all", tags=["standing", "jumping", "fistpump"], alpha=0.3, noother=True)
#  generate_plot_from_file(filename, 23, 24, uids="all", tags=["standing", "fistpump"], xlabel="ax", ylabel="ay", alpha=0.5)
  #  generate_plot_from_file(filename, 1, 22, uids="all", tags=["jumping", "fistpump"], xlabel="frame", ylabel="magnitude")
