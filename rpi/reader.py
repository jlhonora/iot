#!/usr/bin/env python

import json
import os
import serial
import random
import urllib2
import time
from time import gmtime, strftime

# Get any serial port from /dev/
# works in Linux and Mac, should be modified
# for Windows use
def get_serial_port_name():
    tty_str = '/dev/' + os.popen("ls /dev/ | grep -E 'tty(\.usb|USB|AMA)' | head -1").read().strip()    
    return tty_str

# Gets a name for the serial port (if not specified)
# and creates the serial port
def get_serial_port(name = ''):
    if name == '':
        name = get_serial_port_name()
        assert name != '', 'No serial port found'
        print "Automatically selecting %s as serial port" % name
    s = serial.Serial(name, 
                      baudrate     = 57600, 
                      bytesize     = serial.EIGHTBITS, 
                      parity       = serial.PARITY_NONE, 
                      stopbits     = serial.STOPBITS_ONE, 
                      timeout      = 5)
    return s

def safe_open(serial_port):
    if serial_port is None:
        return
    if not serial_port.isOpen():
        serial_port.open()

def post_data(data, url):
    if data is None or len(data) == 0:
        print "Invalid data"
        return
    if data[0] is not '$':
        print "Discarding ", str(data)
        return
    json_data = {
        'payload': data.strip(),
        'received_at': strftime("%Y-%m-%d %H:%M:%S", gmtime())
    }

    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')

    try:
        response = urllib2.urlopen(req, json.dumps(json_data))
        response.close()
    except:
        print "Response failed"

def post_test_data():
    #post_data(str("%d,1,2,255,255,255,255" % random.randint(1, 20)))
    post_data(str("1000,1,2,255,255,255,255"), "http://127.0.0.1:8081")

def run(serial_port = None):
    if serial_port == None:
        serial_port = get_serial_port()
    safe_open(serial_port)
    while True:
        serial_data = serial_port.readline()
        post_data(serial_data, "http://127.0.0.1:8081")
        post_data(serial_data, "http://192.168.0.19:7654/api/v1/iot")
        # uncomment for testing
        #time.sleep(1)
        #post_test_data()

if __name__ == "__main__":
    print "Starting serial port parser"
    run()
    serial_port.close()
    print "Exiting"
