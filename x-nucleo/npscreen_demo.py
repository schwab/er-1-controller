#!/usr/bin/env python
# encoding: utf-8
import sys
import glob
import serial
import npyscreen
import logging
import sys
import curses
#sys.stdout = open('stdout.log', 'w')
sys.stderr = open('stderr.log', 'w')
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
root = logging.getLogger()

class PortTools(object):
    def port_details(self):
        return serial.tools.list_ports.comports()
    def get_ports(self):
        """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

class Options_Form(npyscreen.ActionFormV2WithMenus):
    ports= []
        
    def create(self):
        self.show_atx = 20
        self.show_aty = 5
        pt = PortTools()
        self.ports = pt.get_ports()
        #self.name = self.add(npyscreen.TitleText, name='Name')
        self.serialPort = self.add(npyscreen.TitleSelectOne, max_height=4, \
            values=self.ports, value=[1,], name="Propeller Port")
        self.joyStick= self.add(npyscreen.TitleMultiSelect, max_height =-2, value = [-1,], name="Enable",
                values = ["Joystick"], scroll_exit=True)
        #self.add(npyscreen.MultiLineActionWithShortcuts, max_height=4, value = [1,], name="Pick One", 
        #    values = ["Option1","Option2","Option3"], scroll_exit=True)
        menu_root = self.new_menu()
        menu_root.addItem("test", curses.beep)
        #self.edit()
    def on_ok(self):
        root.info("OK selected on Options form, setting values.`")
    def on_cancel(self):
        root.info("Cancel selected on Options form, ignoring values.")
   
    def afterEditing(self):
        #print "Editing done. %s  %s" %(self.serialPort.get_value(), self.joyStick.get_value())
        self.parentApp.setNextForm(None)

class Motor_Channel(npyscreen.ActionForm, npyscreen.SplitForm, npyscreen.FormWithMenus):
    ports= []
        
    def create(self):
        self.show_atx = 1
        self.show_aty = 1
        pt = PortTools()
        
        self.m1 = self.add_menu(name="Main Menu", shortcut="m")
        self.m1.addItemsFromList([
            ("Options", self.showOption,"^O"),
            ("Connect", self.connect, "^C"),
            ("Exit Application", self.exit_application, "^X"),
        ])
    def showOption(self):
        self.parentApp.setNextForm(Options_Form)
       
    def connect(self):
        root.info("Connect command received.")
   
    def exit_application(self):
        curses.beep()
        self.parentApp.setNextForm(Options_Form)
        self.editing = False
        self.parentApp.switchFormNow()
 
   
    def afterEditing(self):
        #print "Editing done. %s  %s" %(self.serialPort.get_value(), self.joyStick.get_value())
        self.parentApp.setNextForm(None)

class Controller_Application(npyscreen.NPSAppManaged):
    port = None
    options = None
    def onStart(self):
        #pt = PortTools()
        #self.ports = pt.get_ports()
        self.options = self.addForm('MAIN', Motor_Channel, name='Channel 1', lines=25, columns=40, split_at=7)
        
        
    def onCleanExit(self):
        #root.debug("Serial Port selected value : %s", self.options.serialPort.value)
        #root.debug("Joystic selected value : %s", self.options.joyStick.value)
        if self.port:
            self.port.close()

if __name__ == "__main__":
    App = Controller_Application().run()
    
