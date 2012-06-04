#!/usr/bin/env python

from pylab import *
from data import gestures_idmil_230811
import operations.display
import operations.classifier
import operations.pca
import features.basic
import features.blockbased

data = gestures_idmil_230811.load_data()

def get_cors(s,g):
    d = {'time': data[s][g][:,0],
         'accel': data[s][g][:,1:]}
    # d['time'] = d['time'][:1024+16]
    # d['accel'] = d['accel'][:1024+16]
    features.basic.magnitude(d)
    features.basic.hipassed(d,2,0.01)
    sr = 1.0/average(d['time'][1:]-d['time'][:-1])
    freq = 0.8
    features.basic.axes_correlation2d(d,freq/sr*pi*2,arange(10)*100)
    ac = features.blockbased.windowed(d, 'mag',
                                      features.blockbased.autocorrelation,
                                      'autocorrelation',
                                      size=1024, hopsize=16)
    cor = features.blockbased.windowed(d, 'hipassed',
                                       features.blockbased.axes_correlation,
                                       'axes_correlation',
                                       size=1024, hopsize=16)
    cor['tags'] = ['gesture%d'%g] #, 'subject%d'%s]
    features.blockbased.correlation_reduce(cor, 'axes_correlation',
                                           'axes_correlation_reduced')

    cors = {'time': ac['time']}
    cors['autocorrelation'] = ac['autocorrelation']#[:,::10]
    cors['axes_correlation'] = cor['axes_correlation']#[:,::10]
    cors['axes_correlation_reduced'] = cor['axes_correlation_reduced']
    cors['subject'] = s
    cors['tags'] = ['gesture%d'%g] #, 'subject%d'%s]
    return d, cors

def plot_suj_gesture(s,g):
    d, cors = get_cors(s,g)

    subplot(5,4,g*4+1)
    #operations.display.matrixtimeplot(cors, 'autocorrelation')
    plot(cors['autocorrelation'][0])
    subplot(5,4,g*4+2)
    #operations.display.matrixtimeplot(cors, 'axes_correlation')
    #plot(cors['axes_correlation'][0])
    [plot(b,alpha=0.2) for b in cors['axes_correlation']]
    subplot(5,4,g*4+3)
    [plot(b,alpha=0.2) for b in cors['axes_correlation_reduced']]
    subplot(5,4,g*4+4)
    [plot(b,alpha=0.1) for b in d['axes_cor2d']]

def plot_autocor():
    def plot_suj_gest_autocor(s,g):
        d, cors = get_cors(s,g)
    
        subplot(5,1,g*1+1)
        plot(cors['autocorrelation'][0],'k', alpha=0.3)
        xticks([])
        yticks([])
        if (s==0):
            ylabel('Gesture %d'%(g))
    
    for i in range(6):
        for j in range(5):
            plot_suj_gest_autocor(i,j)

def plot_axescor():
    def plot_suj_gest_autocor(s,g):
        d, cors = get_cors(s,g)
    
        subplot(5,1,g*1+1)
        plot(cors['axes_correlation'][0],'k', alpha=0.3)
        xticks([])
        yticks([])
        if (s==0):
            ylabel('Gesture %d'%(g))
    
    for i in range(6):
        for j in range(5):
            plot_suj_gest_autocor(i,j)

def plot_them():
    for i in range(3):
        figure(i+1).clear()
        plot_suj_gesture(i,0)
        plot_suj_gesture(i,1)
        plot_suj_gesture(i,2)
        plot_suj_gesture(i,3)
        plot_suj_gesture(i,4)

def evaluate_with_classifier():
    cs = [get_cors(s,g) for s in range(6) for g in range(5)]
    all_ds, all_cors = zip(*cs)
    [c.pop('autocorrelation') for c in all_cors]
    [c.pop('axes_correlation') for c in all_cors]
    operations.classifier.fann_evaluate_features(all_cors,
                                                 max_iterations=1000,
                                                 num_hidden=10,
                                                 learning_rate=0.95)

    # cs = [get_cors(s,g) for s in range(6) for g in range(5)]
    # all_ds, all_cors = zip(*cs)
    # [c.pop('hipassed') for c in all_ds]
    # [c.pop('accel') for c in all_ds]
    # [c.pop('mag') for c in all_ds]
    # operations.classifier.fann_evaluate_features(all_ds,
    #                                              max_iterations=1000,
    #                                              num_hidden=10,
    #                                              learning_rate=0.95)

def plot_reduced_correlation():
    cs = [get_cors(s,g) for s in range(6) for g in range(5)]
    all_ds, all_cors = zip(*cs)
    figure(1).clear()
    figure(2).clear()
    for cor in all_cors:
        c = 'rgbymk'[int(cor['tags'][0][-1:])]
        d = 'rgbymk'[cor['subject']]
        figure(1)
        plot (cor['axes_correlation_reduced'][:,0],
              cor['axes_correlation_reduced'][:,1],
              '%c-'%c)
        figure(2)
        plot (cor['axes_correlation_reduced'][:,0],
              cor['axes_correlation_reduced'][:,1],
              '%c-'%d)
    figure(1)
    title("Reduced correlation by gesture")
    figure(2)
    title("Reduced correlation by subject")

def plot_axesvs():
    for s in range(6):
        figure(s+1)
        for g in range(5):
            subplot(3,2,g+1)
            d, c = get_cors(s,g)
            plot(d['hipassed'][:,0], d['hipassed'][:,1], color='b')
            plot(d['hipassed'][:,1], d['hipassed'][:,2], color='g')
            plot(d['hipassed'][:,0], d['hipassed'][:,2], color='r')

def plot_accvel():
    from scipy.signal import lfilter
    for i in range(5):
        subplot(3,2,i+1)
        d, c = get_cors(0,i)
        plot(d['hipassed'][:,0],
             lfilter([1],[1,-1],d['hipassed'][:,0]))

tr = []
def plot_pca2():
    cs = [get_cors(s,g) for s in range(6) for g in range(5)]
    all_ds, all_cors = zip(*cs)
    trans = operations.pca.get_pca_transform(all_cors, numpcs=2,
                   feature='axes_correlation')
    tr.append(trans)
    return

    figure(1).clear()
    figure(2).clear()
    for cor in all_cors:
        c = 'rgbymk'[int(cor['tags'][0][-1:])]
        d = 'rgbymk'[cor['subject']]

        # Apply PCA transform
        pcomp = dot(trans, cor['axes_correlation'].T)

        # Take first two components
        figure(1)
        plot(pcomp[0,:], pcomp[1,:], '%co'%c)
        figure(2)
        plot(pcomp[0,:], pcomp[1,:], '%co'%d)
    figure(1)
    title("Axes correlation PCA1+2 by gesture")
    figure(2)
    title("Axes correlation PCA1+2 by subject")

# plot_them()
# plot_autocor()
# plot_axescor()
# plot_reduced_correlation()
plot_pca2()
# evaluate_with_classifier()
# plot_accvel()
# plot_axesvs()
show()
