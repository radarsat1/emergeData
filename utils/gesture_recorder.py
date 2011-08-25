#!/usr/bin/env python

from minibee import Minibees
import sys, serial, time, collections
from pylab import *
from Tkinter import Tk, Canvas
import json
from multiprocessing import Process, Queue, Event

### Options

SECONDS_PER_GESTURE = 30

### End of options

class Logger(object):
    def __init__(self, filename):
        self.qtag = Queue()
        self.done = Event()
        self.tag = None
        self.filename = filename
        self.file = None
    def start(self):
        self.file = open(self.filename, 'w')
        print 'Opened',self.filename,'for writing.'
    def set_tag(self, tag):
        self.qtag.put(tag)
    def set_done(self):
        self.done.set()
    def log(self, nodeid, msgid, data):
        if not self.qtag.empty():
            self.tag = self.qtag.get()
        if self.done.is_set():
            self.done.clear()
            return True
        L = ['%f'%time.time(), '%d'%nodeid, '%d'%msgid] + map(str,data)
        if self.tag:
            L.append(self.tag)
        print >>self.file, ','.join(L)
        self.file.flush()
    def close(self):
        if self.file:
            self.file.close()
            print 'File closed.'

def MBtaskTest(logger):
    logger.start()
    for i in range(30):
        time.sleep(1)
        if logger.log(1, 1, [4,5,6]):
            break
    logger.close()

def MBtask(logger):
    if len(sys.argv) > 1:
        ser = serial.Serial(sys.argv[1])
    else:
        ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 19200
    logger.start()
    Minibees(ser, logger.log, msg_period=100, samps_per_msg=10).run()
    logger.close()

class GUI(object):
    def __init__(self, logger):
        self.logger = logger
        self.root = Tk()
        self.canvas = Canvas(self.root, width=800, height=800)
        self.canvas.pack()
        self.root.after(33, self.update)
        self.pos = (0,0)
        self.circle = self.canvas.create_oval(-10,-10,10,10,fill='black')
        self.gestures = [
            lambda t,x,y,s: ((sin(t*2*pi*0.5)*300 + 400,
                              abs(cos(t*2*pi*0.2)*300) + 200),
                             s),
            lambda t,x,y,s: ((sin(t*2*pi*1)*300 + 400,
                              cos(t*2*pi*1)*300 + 400),
                             s),
            lambda t,x,y,s: ((sin(t*2*pi*0.75)*300 + 400,
                              -abs(cos(t*2*pi*0.75)*300) + 400),
                             s),
            lambda t,x,y,s: ((x+(s[0] - x)*0.1,
                              y+(s[1] - y)*0.1),
                             (uniform(100,700)*(t%1<0.05) + (t%1>0.05)*s[0],
                              uniform(100,700)*(t%1<0.05) + (t%1>0.05)*s[1])),
            lambda t,x,y,s: ((400, y+s[1] if y < 700 else 700-s[1]),
                             (0, (10 + s[1])*(-0.5 if y>700 else 1))),
            ]
        self.state = [0,0]
        self.current_gesture = -1
        self.last_gesture_time = time.time()
        self.next_gesture(self.last_gesture_time)
        self.waiting = True
        self.root.bind('<space>', self.on_space)
        self.logger.set_tag('waiting')

    def on_space(self, *args):
        self.waiting = False
        self.last_gesture_time = time.time()

    def run(self):
        self.root.mainloop()

    def next_gesture(self, t):
        self.current_gesture += 1
        if self.current_gesture >= len(self.gestures):
            self.root.quit()
            self.logger.set_done()
            return True
        else:
            self.last_gesture_time = t
            gestureID = 'gesture%d'%self.current_gesture
            self.logger.set_tag(gestureID)
            print gestureID

    def update(self):
        if not self.waiting:
            t = time.time()
            if (t - self.last_gesture_time) > SECONDS_PER_GESTURE:
                if self.next_gesture(t):
                    return
            pos, self.state = self.gestures[self.current_gesture](t,self.pos[0],self.pos[1],self.state)
            delta = pos[0] - self.pos[0], pos[1] - self.pos[1]
            self.canvas.move(self.circle, delta[0], delta[1])
            self.pos = pos
        self.root.after(33, self.update)

if __name__=='__main__':
    logger = Logger('data.log')
    MBproc = Process(target=MBtask, args=(logger,))
    #MBproc = Process(target=MBtaskTest, args=(logger,))
    MBproc.start()
    gui = GUI(logger)
    gui.run()
    MBproc.join()
