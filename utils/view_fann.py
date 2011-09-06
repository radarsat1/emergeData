#!/usr/bin/env python

from pylab import *
import sys

s = 0
inputs = []
outputs = []
for line in open('/tmp/fann.trainingset'):
    if s==0:
        print line
        s = 1
    elif s==1:
        inputs.append([float(x) for x in line.split()])
        s = 2
    elif s==2:
        outputs.append([float(x) for x in line.split()])
        s = 1

inputs = array(inputs)
outputs = array(outputs)

print inputs.shape, outputs.shape

#subplot(2,1,1)
imshow(inputs.T, cmap='gray', interpolation='nearest')
#subplot(2,1,2)
plot(outputs*inputs.shape[1])
#ylim(outputs.min()*1.1, outputs.max()*1.1)
show()
