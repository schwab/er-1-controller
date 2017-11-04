import serial
import binascii
from sys import stdin
import time 

hold_loop = True
BAUD = 115200
ser = serial.Serial('/dev/ttyUSB1', BAUD, timeout=.9)

print (ser.isOpen())
def read_wait():
    if not ser or not ser.isOpen(): raise Exception("Port not open")
    read = ''
    inp = None
    if ser.inWaiting() > 0:
        buf = ser.read(ser.inWaiting())
        return buf
    return None

try:
    ser.setDTR(1)
    ser.setRTS(1)
    ser.write([serial.CR, serial.LF])
    indec = ""
    while hold_loop:
        time.sleep(.4)
        
        data = read_wait()
        if data:
            lines = filter(None,data.split("\r"))
            for line in lines:
                print(line)
            indec = stdin.readline()
        
            if indec == '\n':
                ser.write([serial.CR, serial.LF])
            elif "X" in indec:
                raise KeyboardInterrupt()
            else:
                indec = indec.replace("\n","").replace("^[[21~","").replace("\x1b[21~", "")
                bytes_to_send = [x for x in indec]
                if bytes_to_send :
                    bytes_to_send.append(serial.CR)
                    bytes_to_send.append(serial.LF)
                    ser.write(bytes_to_send)
                #data = read_wait()
                #if data:
                #    print(data)
        

except KeyboardInterrupt:
    print "closing serial port."
    ser.close()
except Exception as e:
    print e
    ser.close()


    