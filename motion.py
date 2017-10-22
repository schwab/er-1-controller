#from opencv.cv import *
#from opencv.highgui import *


import serial
import time
#import msvcrt
import math
import sys

DEBUG = 1
NOSEND = 0
RIGHT = -2      #This number is arbitrary, but the same as used in oo_remote.py

UPDATE                  = 0x1A
SET_MOTOR_COMMAND       = 0x77
RESET                   = 0x39
SET_LIMIT_SWITCH_MODE   = 0x80
SET_PROFILE_MODE        = 0xA0
SET_ACCELERATION        = 0x90
SET_DECELERATION        = 0x91
SET_JERK                = 0x13
SET_VELOCITY            = 0x11
GET_COMMANDED_POSITION  = 0x1D  #Get Instantaneous Position
SET_ACTUAL_POSITION_UNITS=0xBE
GET_HOST_IO_ERROR       = 0xA4
GET_EVENT_STATUS        = 0x31

LastNumber0 = 0
LastNumber1 = 0

TURNING = 3.
MOVING = 0.5


def hibyte(word):
    return word/256

def lobyte(word):
    return word - (hibyte(word) * 256)

def loword(dword):
    return dword - (hiword(dword) * 65536)

def hiword(dword):
    return dword/65536

def ordIF(s1, s2):
    c = (ord(s1) - ord(s2))
    if c > 9:
        c -= 7
    return c

def toByte(s):
    s = s.upper()
    return (ordIF(s[0], "0")*16) + ordIF(s[1], "0")

class PWDCmd:
    address = 0x0
    #checksum = 0x0
    axis = 0        #Always zero
    code = 0x0
    data = [0xCC,0xCC,0xCC,0xCC,0xCC,0xCC]
    def __init__(self):
        self.data  = [0xCC,0xCC,0xCC,0xCC,0xCC,0xCC]
        self.address = self.checksum = self.axis = self.code = 0x0
    
    def sum_all(self):
        s = sum([self.address, self.get_checksum() ,self.axis, self.code]) + sum(self.get_data())
        return s
    def get_data(self):
        return filter(None,[i for i in self.data if not i == 0xCC])

    def str_bytes(self):
        b = 0
        bset = [''.join('{:02x}'.format(self.address)),
        ''.join('{:02x}'.format(self.get_checksum())),
        ''.join('{:02x}'.format(self.axis)),
        ''.join('{:02x}'.format(self.code))] 
        bset.extend([ " ".join('{:02x}'.format(x) for x in self.get_data())])
        print "Byte length", len(bset)
        print self.sum_all()
        return " ".join(bset) + " sum : " + str("{:02x}".format(self.sum_all()))

    def twos_comp(self, val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return -val 

    def get_checksum(self):
        frame = []
        frame.append(self.address)
        frame.append(0)
        frame.append(self.code) 
        frame.extend([d for d in self.data if not d == 0xCC])
        return self.twos_comp(sum(frame), 8) & 0xFF


class Pos:
    x = 0.
    y = 0.
    theta = 0.      # FROM ZERO TO 2PI, std. unit circle
    CIR_DIST = 10.16*math.pi*4.1 #About 4.1 turns of the wheel, diameter of wheel ~10cm

    #Assumes that diff0 ~= diff1, which is not actually true
    def Adjust(self, diff0, diff1):
        if diff1 == 0 and diff0 == 0:
            pass
        elif (diff1 > 0 and diff0 > 0) or (diff1 < 0 and diff0 < 0):   #forward/backward
            self.x += math.cos(self.theta)*diff0
            self.y += math.sin(self.theta)*diff0
        else:       #turning
            self.theta += (diff0/self.CIR_DIST)*math.pi*2
            while self.theta > math.pi*2.:
                self.theta -= math.pi*2.
            while self.theta < 0:
                self.theta += math.pi*2.

class Robot:
    pos = Pos()
    ser = None

    def __init__(self, port):
        self.InitializeRobot(port)
    
    def SetCmd2(self, byte1, byte2):
        cmd = PWDCmd()
        #cmd.data = [0xCC,0xCC,0xCC,0xCC,0xCC,0xCC]  #for some reason this gets changed in the class, so always reset to default
        cmd.address = byte1
        cmd.code = byte2
        #cmd.checksum = ~(byte1 + byte2) + 1
        #if cmd.checksum < 0:
        #    cmd.checksum += 256
        return cmd

    def SetCmd3(self, byte1, byte2, data1):
        cmd = self.SetCmd2(byte1, byte2)
        cmd.data[0] = hibyte(data1)
        cmd.data[1] = lobyte(data1)
        #cmd.checksum = ~(~(cmd.checksum-1)+ cmd.data[0] + cmd.data[1]) + 1
        #if cmd.checksum < 0:
        #    cmd.checksum += 256
        return cmd

    def SetCmd4(self, byte1, byte2, data1, data2):
        cmd = self.SetCmd3(byte1, byte2, data1)
        cmd.data[2] = hibyte(data2)
        cmd.data[3] = lobyte(data2)
        #cmd.checksum = ~(~(cmd.checksum-1)+ cmd.data[2] + cmd.data[3]) + 1
        #if cmd.checksum < 0:
        #    cmd.checksum += 256
        return cmd

    def SendCmd(self, cmd):
        reply = ""
        if not NOSEND:
            bytes = ""
            bytes += chr(cmd.address)
            bytes += chr(cmd.get_checksum())
            bytes += chr(cmd.axis)
            bytes += chr(cmd.code)
            for b in cmd.data:
                if b < 0:
                    b += 256
                if b != 0xCC:       # For whatever reason 0xCC is "null" -> we could fix this by keeping track of size...
                    bytes += chr(b)
            self.ser.write(bytes)
            time.sleep(0.03)        # Wait for response to be created
            reply = self.ser.read(size=8)
                
        if DEBUG:
            print "DEBUG..."
            print cmd.str_bytes()
        #    bytes = "SENT : "
        #    #bytes += str(cmd.address)
	    #bytes += ''.join('{:02x}'.format(cmd.address))
        #    bytes += " "
        #    #bytes += str(cmd.checksum)
	    #bytes += ''.join('{:02x}'.format(cmd.checksum))
        #    bytes += " "
        #    #bytes += str(cmd.axis)
	    #bytes += ''.join('{:02x}'.format(cmd.axis))
        #    bytes += " "
	    #bytes += ''.join('{:02x}'.format(cmd.code))
        #    #bytes += str(cmd.code)
        #    bytes += " "
	    #bytes += ''.join('{:02x}'.format(x) for x in cmd.data)		
        #    #for b in cmd.data:
        #    #    if b < 0:
        #    #        b += 256
        #    #    bytes += str(b) + " "
        #    print bytes
            if not NOSEND:
                #newstring = "Reply bytes : ", len(reply)
                #for s in reply:
                #    newstring += str(ord(s)) + " "
                print "Reply string: ", [str(ord(x)) for x in reply] , "len ", len(reply)
        return reply

    def SendCmd2(self, byte1, byte2):
        return self.SendCmd(self.SetCmd2(byte1, byte2))

    def SendCmd3(self, byte1, byte2, data1):
        return self.SendCmd(self.SetCmd3(byte1, byte2, data1))

    def SendCmd4(self, byte1, byte2, data1, data2):
        return self.SendCmd(self.SetCmd4(byte1, byte2, data1, data2))

    def WheelUpdate(self):
        self.SendCmd2(1,UPDATE)
        self.SendCmd2(0,UPDATE)

    def WheelSetPower(self, data):
        self.SendCmd3(1, SET_MOTOR_COMMAND, data)
        self.SendCmd3(0, SET_MOTOR_COMMAND, data)

    def WheelInit(self):
        self.SendCmd2(1, RESET)
        self.SendCmd3(1, SET_LIMIT_SWITCH_MODE, 0x0000)
        self.SendCmd3(1, SET_MOTOR_COMMAND, 0x0000)
        self.SendCmd3(1, SET_PROFILE_MODE, 0x0001)
        self.SendCmd4(1, SET_ACCELERATION, 0x0000, 0x00B0)
        self.SendCmd4(1, SET_DECELERATION, 0x0000, 0x00B0)
        self.SendCmd4(1, SET_JERK, 0x0329, 0x0ABB)

        self.SendCmd2(0, RESET)
        self.SendCmd3(0, SET_LIMIT_SWITCH_MODE, 0x0000)
        self.SendCmd3(0, SET_MOTOR_COMMAND, 0x0000)
        self.SendCmd3(0, SET_PROFILE_MODE, 0x0001)
        self.SendCmd4(0, SET_ACCELERATION, 0x0000, 0x00B0)
        self.SendCmd4(0, SET_DECELERATION, 0x0000, 0x00B0)
        self.SendCmd4(0, SET_JERK, 0x0329, 0x0ABB)

        self.WheelUpdate()

    def WheelSetVelocity(self, dwSpeed):
        dwNegSpeed = ~dwSpeed + 1
        self.WheelSetPower(0x4CC0)
        self.SendCmd4(1, SET_VELOCITY, hiword(dwNegSpeed), loword(dwNegSpeed))
        self.SendCmd4(0, SET_VELOCITY, hiword(dwSpeed), loword(dwSpeed))

    def WheelSetTurn(self, dwSpeed):    # + is left, neg is right
        self.WheelSetPower(0x4CC0)
        self.SendCmd4(1, SET_VELOCITY, hiword(dwSpeed), loword(dwSpeed))
        self.SendCmd4(0, SET_VELOCITY, hiword(dwSpeed), loword(dwSpeed))

    def GetPos(self):
        # In theory, these results are in counts, not that we know (yet) what they mean!
        # But the numbers are so large, they must be in microsteps...
        reply = self.SendCmd2(1, GET_COMMANDED_POSITION)
        number1 = 0
        i = 3
        for s in reply[2:5]:
            number1 += ord(s)*(256**i)
            i -= 1
        number1 = -number1
        number1 += 0xFFFFFFFF
        if number1 > (0xFFFFFFFF/2): #Due to the limit of the PMD processor, we only have a ulong. So, half is pos, half is neg.
        # That is to say, we are using two's complement arithmetic on a 16-bit processor. 
            number1 -= 0xFFFFFFFF
        number1 /= 64.       # Number of microsteps per electrical cycle
        number1 /= 256.      # Number of steps?
        
        reply = self.SendCmd2(0, GET_COMMANDED_POSITION)
        number0 = 0
        i = 3
        for s in reply[2:5]:
            number0 += ord(s)*(256**i)
            i -= 1
        if number0 > (0xFFFFFFFF/2):
            number0 -= 0xFFFFFFFF
        number0 /= 64.       # Number of microsteps per electrical cycle
        number0 /= 256.
        
        global LastNumber0, LastNumber1
        diff1 = number1 - LastNumber1
        diff0 = number0 - LastNumber0
        diff1 *= 10.16*math.pi/3.28
        diff0 *= 10.16*math.pi/3.28

        LastNumber1 = number1
        LastNumber0 = number0
        self.pos.Adjust(diff0, diff1)

    def PrintPos(self):
        self.GetPos()
        string = "Position: " + str(self.pos.x) + " " + str(self.pos.y) + " " + str(self.pos.theta)
        print string

    def InitializeRobot(self, PORT):
        self.ser = serial.Serial(PORT,  9600, )
        self.ser.baudrate =  9600
        self.ser.timeout = 0
        #ser.open()
        
        if not self.ser.isOpen():
            print "ERROR OPENING ROBOT PORT"
            sys.exit(-1)
        print "Opened Port : " , self.ser.name
        self.WheelInit()

    def Go(self, speed):   #Speed is cm/s
        self.WheelSetVelocity(int(speed*16700))
        self.WheelUpdate()
        self.GetPos()

    def GoDist(self, dist, speed=10.):   #dist in cm
        if dist < 0 and speed > 0:
            speed = -speed
        startX = curX = self.pos.x
        startY = curY = self.pos.y
        while abs(dist) - math.sqrt((startX-curX)**2 + (startY-curY)**2) > abs(speed)/2.5:
            self.Go(speed)
            self.GetPos()
            curX = self.pos.x
            curY = self.pos.y
        self.Go(0)

    def Turn(self, speed, direction):
        if direction == RIGHT:
            speed = -speed
        self.WheelSetTurn(int(speed*16700))
        self.WheelUpdate()
        self.GetPos()

    def TurnAngle(self, radians, direction, speed=8.):
        if direction == RIGHT:
            radians = -radians
        wantTh = radians + self.pos.theta
        while wantTh > math.pi*2.:
            wantTh -= math.pi*2.
        while wantTh < 0.:
            wantTh += math.pi*2.
        curTh = self.pos.theta
        while abs(wantTh - curTh) > (math.pi*2./self.pos.CIR_DIST) * speed/2.5:
            self.Turn(speed, direction)
            self.GetPos()
            curTh = self.pos.theta
        self.Turn(0, direction)

    def GetRobotPos(self):
        self.GetPos()
        string = str(self.pos.x) + " " + str(self.pos.y) + " " + str(self.pos.theta)
        return string
        
    def CloseRobot(self):
        self.WheelSetVelocity(0x0)
        self.WheelUpdate()
        self.WheelSetPower(0x0)
        self.ser.close()
    def GetIoError(self):
        reply = self.SendCmd2(0,GET_HOST_IO_ERROR)
        print "IOERROR 0:", reply
        reply = self.SendCmd2(1,GET_HOST_IO_ERROR)
        print "IOERROR 1: ", reply
    def GetEventStatus(self):
        reply = self.SendCmd2(0, GET_EVENT_STATUS)
        print "Event Status 0:", reply
        reply = self.SendCmd2(1, GET_EVENT_STATUS)
        print "Event Status 1: ", reply
