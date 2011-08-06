#!/usr/bin/env python2.6

import sys
from progressbar import ProgressBar
from generate_plot_from_file import load_column_names
from minibees_common import read_tags

if (len(sys.argv) != 5):
  print "Usage: " + sys.argv[0] + " <inputfile> <tags> <n> <outputfile>"
  exit(0)

inputfile = sys.argv[1]
if (sys.argv[2] == "all"):
  t = read_tags()
  tags = t.all_tags
else:
  tags = sys.argv[2].split(",")
print tags
n = int(sys.argv[3])
outputfile = sys.argv[4]

columnNames = load_column_names(inputfile)
tagsIdx = map(lambda x: columnNames.index(x), tags)
print tagsIdx

print "Opening files"
f = open(inputfile, "r")
nOther = 0
nPositive = []
for i in range(len(tags)):
  nPositive.append(0)

outf = open(outputfile, "w")

print "Processing"
lines = f.readlines()
nLines = len(lines)-1
outf.write(lines[0]) # comment line
del lines[0]

pbar = ProgressBar(0, nLines, mode='static')
pbar.update()
for line in lines:
  arr = map(lambda x: float(x), line.replace("\n","").split())
  noPositive = True
  addLine = False
  allFull = True
  for i, idx in enumerate(tagsIdx):
    if (nPositive[i] < n):
      allFull = False
    if (arr[idx] == 1):
      if (nPositive[i] < n):
        nPositive[i] += 1
        addLine = True
        noPositive = False
  if (nOther < n):
    allFull = False
    if (noPositive):
      nOther += 1
      addLine = True

  if addLine:
    outf.write(line)
    
  if (allFull):
    pbar.update(nLines)
    break
  else:
    pbar.increment()

pbar.finish()
  
print "All done."
f.close()
outf.close()    