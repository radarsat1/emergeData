#!/usr/bin/env python2.6

from pylab import *
from numpy import vstack
import sys

from collections import defaultdict

from pybrain.datasets import *
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer
from pybrain.utilities import percentError

from pybrain.tools.xml.networkwriter import NetworkWriter
from pybrain.tools.xml.networkreader import NetworkReader

from minibees_common import *
from generate_plot_from_file import load_column_names, load_data

N_HIDDEN = 3
LEARNING_RATE = 0.1
LEARNING_RATE_DECAY = 0.01

def normalize_columns(arr):
    rows, cols = arr.shape
    for col in xrange(cols):
        arr[:,col] /= abs(arr[:,col]).max()

def create_data_set(data, columnNames, inputs, tag):
  from pprint import pprint
  inputsIdx = []
  for x in inputs:
    inputsIdx.append(columnNames.index(x))
  tagIdx   = columnNames.index(tag)
  ds = SupervisedDataSet(len(inputs), 1)
  nrows = data.shape[0]
  ncols = data.shape[1]
  nInputs = len(inputsIdx)
  
  inputData = data[:, inputsIdx[0]]
  for i in range(1, nInputs):
    inputData = vstack( (inputData, data[:,inputsIdx[i]]))
  inputData = inputData.reshape(nrows, nInputs)
  normalize_columns(inputData)
  targetData = data[:,tagIdx].reshape(nrows, 1)
  assert(inputData.shape[0] == targetData.shape[0])
  ds.setField('input', inputData)
  ds.setField('target', targetData)
  return ds

def threshold(x):
  if (x > 0.5):
    return 1
  else:
    return 0

def relativePercentError(out, true):
  nPositive = true.sum()
  if (nPositive > true.size / 2):
    nPositive = true.size - nPositive # take only the smallest
  propErrorRandom = nPositive / float(true.size)
  print "n positive = " + str(nPositive)
  print "size = " + str(true.size)
  percentErrorAbs = percentError(out, true)
  print "% error " + str(percentErrorAbs)
  print "p error rnd " + str(propErrorRandom)
  return percentErrorAbs / propErrorRandom
  
def testOnClassData(trainer):
  # Make plot
  ds = trainer.ds
  net = trainer.module
  activations = []
  for i in range(0, len(ds['input'])):
    out = threshold(net.activate( ds['input'][i] ))
    activations.append(out)
  return activations
  
def main():
  # Create dataset
  
  inputs = ["jrms", "rms", "mean_10", "mean_100", "max_10", "max_100", "stddev_10", "stddev_100"]
#  inputs = ["max_100", "rms"]
#  inputs = ["max_100", "mean_100"]
#  inputs = ["rms"]
  mode = "train"

  if (len(sys.argv) >= 2):
    if (sys.argv[1] == "test"):
      mode = "test"
  
  print "Create dataset"
  data = load_data("out.txt")
  columnNames = load_column_names("out.txt")
  ds = create_data_set(data, columnNames, inputs, "jumping")
  
  targets = ds['target']
  #print "sum of targest: " + str(targets.sum())
  
  # Create network
  if (mode == "train"):
    print "Build network"
    if (len(sys.argv) >= 3):
      nEpochs = int(sys.argv[2])
    else:
      nEpochs = 1
    net = buildNetwork(len(inputs), N_HIDDEN, 1, bias=True, hiddenclass=TanhLayer)
    trainer = BackpropTrainer(net, ds, verbose = True)
    #net = buildNetwork(len(inputs), N_HIDDEN, 1, bias=True, hiddenclass=TanhLayer)

    print "Train"
    print "Base error: " + str(trainer.testOnData())
    results = testOnClassData(trainer)
    print "Percentage error: " + str(relativePercentError( results, targets )) + "%"
    print "Training started"
    trainer.trainEpochs(nEpochs)
    print "Training done: Saving model"
    NetworkWriter.writeToFile(net, "model.xml")
  else:
    net = NetworkReader.readFrom("model.xml")
    trainer = BackpropTrainer(net, ds, verbose = True)
  
  #print "Final error: " + str(trainer.testOnData())
  
  results = testOnClassData(trainer)
  print "Percentage error (final): " + str(relativePercentError( results, targets )) + "%"
  
  
  # Plot
  # Data
  frames = data[:,1]
  nplots = 3
  subplot(nplots, 1, 1)
  dataType = inputs[0]
  title("Data (" + dataType + ")")
  setp(plot(frames, ds['input'][:,0], color="black", marker=".", linestyle='None'))
  xlabel("frame")
  ylabel(dataType)
#  nplots = len(inputs) + 2
#  for i in range(0, len(inputs)):
#    subplot(nplots, 1, i+1)
#    dataType = inputs[i]
#    title("Data (" + dataType + ")")
#    setp(plot(frames, ds['input'][:,i], color="black", marker=".", linestyle='None'))
#    xlabel("frame")
#    ylabel(inputs[i])
  
  # Correct classification (target)
  subplot(nplots, 1, nplots-1)
  title("Target classification")
  targets = targets[:,0]
  setp(plot(frames, targets, color="blue"))

  # Classification (from NN)
  subplot(nplots, 1, nplots)
  title("NN classification and errors")
  setp(plot(frames, results), color="blue")
  errors = [[],[]]
  for i in range(len(results)):
    if (results[i] != targets[i]):
      errors[0].append(frames[i])
      errors[1].append(0.5)
  setp(plot(errors[0], errors[1]), color="red", marker='.', linestyle='None', alpha=0.5)
  
  savefig("figure.png")
  # Neural net classification
  #show()
#
#  trnresult = percentError( trainer.testOnClassData(),
#                              trndata['class'] )
#    tstresult = percentError( trainer.testOnClassData(
#           dataset=tstdata ), tstdata['class'] )
#
#    print "epoch: %4d" % trainer.totalepochs, \
#          "  train error: %5.2f%%" % trnresult, \
#          "  test error: %5.2f%%" % tstresult

if __name__=='__main__':
  main()
