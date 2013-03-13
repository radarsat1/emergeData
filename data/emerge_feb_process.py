
from pylab import *

recording = [open('emerge_feb16.txt','r').readlines(),
             open('emerge_feb17.txt','r').readlines(),
             (open('emerge_feb16.txt','r').readlines()
              + open('emerge_feb17.txt','r').readlines())][1]

rawtimes = []
data = []
logons = []
logoffs = []
loggedin = dict([(i,(False,[])) for i in range(40)])
pcadata = dict([(i,[]) for i in range(40)])
t0 = None
totalloggedin = []
for line in recording:
    line = line.split()
    t = int(line[0]) + float(line[1])/float(1<<32)

    # Time in hours since start
    if (t0 == None): t0 = t
    t = (t-t0)/60/60

    if len(line)>3 and line[2] == 'list' and line[3] == 'ifff':
        rawtimes.append(t)
        idnum = int(line[4])
        if (loggedin[idnum][0]):
            loggedin[idnum][1].append((t, float(line[5]),
                                       float(line[6]),
                                       float(line[7])))
    if len(line)>3 and line[2] == '/logon':
        idnum = int(line[4])
        state = int(line[5])
        if state == 1:
            loggedin[idnum] = (True, [])
            logons.append([t, idnum, state])
        else:
            if (loggedin[idnum][0]) and len(loggedin[idnum][1])>0:
                print 'time logged in', loggedin[idnum][1][-1][0] - loggedin[idnum][1][0][0]
                pcadata[idnum].append(loggedin[idnum][1])
            loggedin[idnum] = (False, [])
            logoffs.append([t, idnum, state])
        totalloggedin.append( sum([loggedin[l][0] for l in loggedin]) )

rawtimes = array(rawtimes)
logons = array(logons)
logoffs = array(logoffs)

print 'Total logged in, avg:',average(totalloggedin),'std:',std(totalloggedin),'max:',max(totalloggedin)

for i in pcadata.keys():
    for n,d in enumerate(pcadata[i]):
        pcadata[i][n] = array(d)

# scatter(rawtimes, rawtimes)
# show()

figure(1)
scatter(logons[:,0], logons[:,1], c='b')
scatter(logoffs[:,0], logoffs[:,1], c='r')
xlabel('Time (hours)')
ylabel('ID')

figure(2)
m = float(max(pcadata.keys()))
for i in pcadata.keys():
    for d in pcadata[i]:
        subplot(311)
        plot(d[:,0], d[:,1], color=cm.prism(i/m))
        subplot(312)
        plot(d[:,0], d[:,2], color=cm.prism(i/m))
        subplot(313)
        plot(d[:,0], d[:,3], color=cm.prism(i/m))
subplot(311); ylabel('PC 1')
subplot(312); ylabel('PC 2')
subplot(313); ylabel('Ampl')

figure(3)
for i in pcadata.keys():
    for d in pcadata[i]:
        scatter(d[:,1], d[:,2], color=cm.prism(i/m))
xlabel('PC 1')
ylabel('PC 2')

show()
