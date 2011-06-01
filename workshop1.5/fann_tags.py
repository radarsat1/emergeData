#!/usr/bin/env python

"""Use accelerometer characteristics to match tags by using a neural
network via FANN."""

from pylab import *
from charactercurves import calc_curves
from read_minibees import read_minibees, mag
from read_tags import read_tags
from export_audio import find_offsets, split_data_on_offsets
import pyfann.libfann as fann

MINIBEE = 7
VIDEO = 1     # 0 or 1
FIELD = 5     # x=5, y=6, z=7

# How many data points to train on?  Will be extracted periodically
# from data set.
TRAIN_EVERY = 10

# Fields from "charactercurves.py" extracted from raw data to use for
# training.  Currently: avg, rms, freq, periodicity
inputfields = ['rms', 'periodicity']

########## Load and calculate data

# minibees, fields = read_minibees()
data = minibees[MINIBEE]
offsets = find_offsets(data)
d = split_data_on_offsets(data, offsets)
curves = calc_curves((d[VIDEO][:,4]-d[VIDEO][0,4])/30.0,
                     d[VIDEO][:,FIELD], 0.1)

tags = read_tags()

frames = curves['time']*30
frametags = [tags.frame_tags(int(d[1][0,3]), f) for f in frames]

def normalized(x):
    return (x - min(x)) / (max(x)-min(x))

target = normalized(array([1.0 if 'fistpump' in t else
                           0.0
                           for t in frametags]))

trainingframes = frames[::TRAIN_EVERY]
trainingset = target[::TRAIN_EVERY]

########## FANN

inputs = [normalized(curves[f]) for f in inputfields]

datafile = open('fann.trainingset','w')
print >>datafile, len(trainingframes), len(inputs), 1
for n, f in enumerate(trainingframes):
    f = int(f)
    print >>datafile, ' '.join([str(x) for x in [inputs[i][n*TRAIN_EVERY]
                                                 for i in range(len(inputs))]])
    print >>datafile, trainingset[n]
datafile.close()

print 'Training.'

connection_rate = 1
learning_rate = 0.97
num_hidden = 7
num_output = 1

desired_error = 0.001
max_iterations = 1000
iterations_between_reports = 10

net = fann.neural_net()

cascade = 'cascade' in sys.argv[2:]
if cascade:
    net.create_shortcut_array((len(inputs), num_output))

    net.set_activation_function_output(fann.LINEAR_PIECE_SYMMETRIC)

    net.cascadetrain_on_file("fann.trainingset", num_hidden, 1, desired_error)

else:
    net.create_sparse_array(connection_rate,
                            (len(inputs), num_hidden, num_output))

    net.set_learning_rate(learning_rate)
    # net.set_activation_function_output(fann.COS_SYMMETRIC)
    # net.set_activation_function_output(fann.SIGMOID_SYMMETRIC)
    net.set_activation_function_output(fann.SIGMOID_STEPWISE)
    # net.set_activation_function_output(fann.GAUSSIAN_SYMMETRIC)
    # net.set_activation_function_output(fann.ELLIOT_SYMMETRIC)
    # net.set_activation_function_output(fann.LINEAR)
    # net.set_activation_function_output(fann.LINEAR_PIECE_SYMMETRIC)

    net.train_on_file("fann.trainingset", max_iterations,
                      iterations_between_reports,
                      desired_error)

net.save("fann.net")

## Execute

print 'Testing.'

out = zeros(inputs[0].shape[0])
for i in xrange(len(inputs[0])):
    out[i] = net.run([inp[i] for inp in inputs])[0]

## Plot results and the inputs

clf()
subplot(1+len(inputs),1,1)
plot(out, 'b')
plot(target, 'r', label='target')
title('output vs. training: minibee %d, tag=fistpump'%MINIBEE)
ylabel('output')
axis(ymax=1.1)

for I in range(len(inputs)):
    subplot(1+len(inputs),1,I+2)
    plot(inputs[I][::TRAIN_EVERY])
    ylabel(inputfields[I])
    scale = max(inputs[I][::TRAIN_EVERY]) / max(trainingset)
    # plot(trainingset*scale, label='training')

show()
