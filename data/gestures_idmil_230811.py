
data = loadtxt('../data/gestures_idmil_230811.csv.bz2', delimiter=',', skiprows=1)

subject = [array([d[0:7] for d in data if d[7]==(s+1)]) for s in range(6)]

sr = 100

def plot_subject(s):
    subplot(6,1,s+1)
    t0 = subject[s][0,0]
    t1 = min([subject[s][k,0] for k in range(subject[s].shape[0])
              if subject[s][k,6]==1])
    tL = subject[s][-1,0]
    time = arange(subject[s].shape[0]) + t1/100

    # Visualize dropped packets
    plot([0 if t == -2559.0 else t
          for t in (subject[s][1:,2]-subject[s][:-1,2])])

clf()

[plot_subject(s) for s in range(6)]
