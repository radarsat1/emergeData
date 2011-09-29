#!/usr/bin/env python

import pyfann.libfann as fann
from pylab import *

def fann_evaluate_features(blocks, max_iterations=1000,
                           num_hidden=7, learning_rate=0.97):
    features = list(set([k for b in blocks for k in b.keys()]).difference(
            set(['time','subject','tags'])))

    count = sum([b['time'].shape[0] for b in blocks])

    tags = dict([(y,x) for (x,y) in
                list(enumerate(set([t for b in blocks
                                    for t in b['tags']])))])

    vecwidths = {}
    for f in features:
        for b in blocks:
            if not vecwidths.has_key(f) and b.has_key(f):
                vecwidths[f] = 1 if len(b[f].shape)==1 else b[f].shape[1]
    total_vecwidth = sum([vecwidths[f] for f in features])

    datafile = open('/tmp/fann.trainingset','w')
    print >>datafile, count/3, total_vecwidth, len(tags)

    for b in blocks:
        for i in range(b['time'].shape[0])[::3]:
            for f in features:
                if b.has_key(f):
                    d = b[f][i,:]
                    if any(isnan(d)):
                        raise Exception("NaN found in feature vector")
                    print >>datafile, ' '.join([str(x) for x in d]),
                else:
                    print >>datafile, ' '.join(['0']*vecwidths[f])
            print >>datafile
            print >>datafile, ' '.join([str(int(t in b['tags'])*2-1)
                                        for t in tags])
    datafile.close()

    connection_rate = 1

    desired_error = 0.00001
    iterations_between_reports = 10

    net = fann.neural_net()

    net.create_sparse_array(connection_rate,
                            (total_vecwidth, num_hidden, len(tags)))

    net.set_learning_rate(learning_rate)

    # net.set_activation_function_output(fann.COS_SYMMETRIC)
    # net.set_activation_function_output(fann.GAUSSIAN)
    net.set_activation_function_output(fann.SIGMOID_SYMMETRIC)
    # net.set_activation_function_output(fann.SIGMOID)
    # net.set_activation_function_output(fann.SIGMOID_STEPWISE)
    # net.set_activation_function_output(fann.GAUSSIAN_SYMMETRIC)
    # net.set_activation_function_output(fann.ELLIOT_SYMMETRIC)
    # net.set_activation_function_output(fann.LINEAR)
    # net.set_activation_function_output(fann.LINEAR_PIECE_SYMMETRIC)
    # net.set_activation_function_output(fann.THRESHOLD)
    # net.set_activation_function_output(fann.THRESHOLD_SYMMETRIC)

    net.train_on_file("/tmp/fann.trainingset", max_iterations,
                      iterations_between_reports,
                      desired_error)

    net.save("fann.net")

    for b in blocks:
        out = []
        for i in xrange(b['time'].shape[0]):
            v = []
            for f in features:
                if b.has_key(f):
                    d = b[f][i,:]
                    v += list(d)
                else:
                    v += [0]*vecwidths[f]
            out.append(net.run(v))
        b['fann_output'] = array(out)

    gesture_tags = [t for t in tags.keys() if 'gesture' in t]
    for b in blocks:
        for n,t in enumerate(gesture_tags):
            subplot(len(gesture_tags),1,n+1)
            fill_between([b['time'][0], b['time'][-1]],
                         [int(t in b['tags'])*2-1]*2, [0]*2,
                         color='#5555FF')
            plot(b['time'], b['fann_output'][:,tags[t]], 'r.')
            ylabel(t)
            ylim(-1.1,1.1)
    show()
