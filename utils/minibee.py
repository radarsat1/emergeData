#!/usr/bin/env python

"""A Python replacement for the minibee Max patch."""

import serial
import time
import sys

def slipdecoder(ser,delim='\n',esc='\\'):
    a = ''
    while (1):
        c = ser.read(1)
        if c==delim:
            yield a
            a = ""
        elif c==esc:
            a += ser.read(1)
        else:
            a += c

def slipencoder(ser,delim='\n',esc='\\'):
    while (1):
        a = yield None
        msg = esc + a.replace(delim,esc+delim) + delim
        ser.write(msg)

class Minibees(object):
    def __init__(self, ser, datafunc=None, msg_period=100, samps_per_msg=1):
        self.inp = slipdecoder(ser)
        self.outp = slipencoder(ser)
        self.outp.next()
        self.datafunc = datafunc
        self.msg_period = msg_period
        self.samps_per_msg = samps_per_msg

        self.nodes = {}
        self.serials = {}

        def nextNodeID(nextid=1):
            while True:
                yield nextid
                nextid = (nextid + 1)%256
        self.nodeids = nextNodeID()

        def nextMsgID(nextid=1):
            while True:
                yield nextid
                nextid = (nextid + 1)%256
        self.msgids = nextMsgID()

    def run(self):
        while True:
            try:
                line = self.inp.next()
                {
                    's': self.on_serial,
                    'w': self.on_waiting,
                    'c': self.on_confirm,
                    'd': self.on_data,
                    }[line[0]](line)
            except KeyError:
                print >>sys.stderr, 'error:',line

    def on_serial(self, line):
        """Node announced itself, it's waiting for an ID assignment. Add it to our local list of nodes."""
        nodeser = line[1:15]
        libver = ord(line[15])
        boardrev = line[16]
        caps = ord(line[17])
        if self.serials.has_key(nodeser):
            nodeid = self.serials[nodeser]
        else:
            nodeid = self.nodeids.next()
            self.serials[nodeser] = nodeid
        self.nodes[nodeid] = {
            'id': nodeid,
            'serial': nodeser,
            'library_version' : libver,
            'board_revision' : boardrev,
            'enable_ping' : caps & 0x04,
            'enable_sht' : caps & 0x02,
            'enable_twi' : caps & 0x01,
            'config_id' : nodeid,
            'description' : 'generic',
            'sample_period' : self.msg_period,
            'samps_per_msg' : self.samps_per_msg,
            'pin_config' : [4,0,4,4,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0],
            'msgID' : 0,
            }
        if boardrev=='B':
            self.nodes[nodeid]['description'] = 'generic RevB'
            self.nodes[nodeid]['pin_config'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,9,0,0]
        self.send_nodeid(self.nodes[nodeid])

    def on_waiting(self, line):
        """Node is waiting for configuration.  Send it a configuration."""
        nodeid = ord(line[1])
        configid = ord(line[2])
        self.send_nodeconfig(self.nodes[nodeid])

    def on_confirm(self, line):
        """Node is confirming that it received configuration."""
        nodeid = ord(line[1])
        configid = ord(line[2])
        smpMsg = ord(line[3])
        msgInt = ord(line[4])
        dataSize = ord(line[5])
        outSize = ord(line[6])
        custom = line[7:]
        print >>sys.stderr, 'confirm node %d:'%nodeid
        print >>sys.stderr, '  configid =', configid
        print >>sys.stderr, '  smpMsg =', smpMsg
        print >>sys.stderr, '  msgInt =', msgInt
        print >>sys.stderr, '  dataSize =', dataSize
        print >>sys.stderr, '  outSize =', outSize
        print >>sys.stderr, '  custom =', custom

    def on_data(self, line):
        """Node is sending a data packet."""
        if self.datafunc:
            d = [ord(x) for x in line[1:]]
            nodeid = d[0]
            msgid = d[1]
            data = [(i|(j&0x80 and (256-j)*-256 or j*256))
                    for i,j in zip(d[2::2],d[3::2])]
            m = msgid * len(data)/3
            #print 'data','len=%d'%len(d),d
            [self.datafunc(nodeid, m+i/3, data[i:i+3])
             for i in range(0,len(data),3)]
        else:
            print 'data', line[1:]

    def send_nodeid(self, node):
        self.outp.send('I%c%s%c%c'%(self.msgids.next(), node['serial'],
                                    node['id'], node['id']))

    def send_nodeconfig(self, node):
        self.outp.send('C%c%c%c%c%c%s'%(self.msgids.next(), node['id'],
                                        node['sample_period']/256,
                                        node['sample_period']%256,
                                        node['samps_per_msg'],
                                        ''.join([chr(x) for x in
                                                 node['pin_config']])))

if __name__=='__main__':
    import time

    if len(sys.argv) > 1:
        ser = serial.Serial(sys.argv[1])
    else:
        ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 19200

    def with_data(nodeid, msgid, d):
        print >>sys.stderr, '.',
        print time.time(), nodeid, msgid, d

    Minibees(ser, with_data, msg_period=350, samps_per_msg=14).run()
