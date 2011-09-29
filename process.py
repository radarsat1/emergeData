#!/usr/bin/env python

from pylab import *
from data import gestures_idmil_230811
import operations.display
import operations.classifier
import features.basic
import features.blockbased

data = gestures_idmil_230811.load_data()

def get_cors(s,g):
    d = {'time': data[s][g][:,0],
         'accel': data[s][g][:,1:]}
    features.basic.magnitude(d)
    features.basic.hipassed(d,2,0.2)
    ac = features.blockbased.windowed(d, 'mag',
                                      features.blockbased.autocorrelation,
                                      'autocorrelation',
                                      size=1024, hopsize=16)
    cor = features.blockbased.windowed(d, 'hipassed',
                                       features.blockbased.axes_correlation,
                                       'axes_correlation',
                                       size=1024, hopsize=16)
    cors = {'time': ac['time']}
    cors['autocorrelation'] = ac['autocorrelation'][:,::10]
    cors['axes_correlation'] = cor['axes_correlation'][:,::10]
    cors['subject'] = s
    cors['tags'] = ['gesture%d'%g] #, 'subject%d'%s]
    return cors

def plot_suj_gesture(s,g):
    cors = get_cors(s,g)

    subplot(5,2,g*2+1)
    operations.display.matrixtimeplot(cors, 'autocorrelation')
    subplot(5,2,g*2+2)
    operations.display.matrixtimeplot(cors, 'axes_correlation')

def plot_them():
    for i in range(3):
        figure(i+1)
        plot_suj_gesture(i,0)
        plot_suj_gesture(i,1)
        plot_suj_gesture(i,2)
        plot_suj_gesture(i,3)
        plot_suj_gesture(i,4)

def evaluate_with_classifier():
    all_cors = [get_cors(s,g) for s in range(6) for g in range(5)]
    [c.pop('autocorrelation') for c in all_cors]
    [c.pop('axes_correlation') for c in all_cors]
    operations.classifier.fann_evaluate_features(all_cors,
                                                 max_iterations=1000,
                                                 num_hidden=10,
                                                 learning_rate=0.95)

plot_them()
evaluate_with_classifier()
show()
