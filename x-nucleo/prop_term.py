import serial
import time   #timing methods
from sys import stdin
port  = '/dev/ttyUSB0'
in_loop = True
try:
    s = serial.Serial(port,timeout=0.9, baudrate=57600,parity=serial.PARITY_EVEN, rtscts=1)
except serial.serialutil.SerialException:
    print "Could not open sp"

if not s.isOpen():
    print "ERROR opening port %s" % (port)
else:
    s.write(0)
    while in_loop:
        l = s.read(100)
        print "term text len %s : %s" % (len(l), l)
        print "input command or exit : "
        input_text = stdin.readline()
        if "exit" in input_text :
            in_loop = False
        else:
            s.write(int(input_text))

        lines = s.read()
        if lines:
            print "len result %s : %s" % (len(lines), lines)
s.close()