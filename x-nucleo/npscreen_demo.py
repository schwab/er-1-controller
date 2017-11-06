#!/usr/bin/env python
# encoding: utf-8
import sys
import glob
import serial
import npyscreen
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
#class TestApp(npyscreen.NPSApp):
#    ports = []
#    def __init__(self):
#        pt = PortTools()
#        self.ports = pt.get_ports()
#    def main(self):
#        # These lines create the form and populate it with widgets.
#        # A fairly complex screen in only 8 or so lines of code - a line for each control.
#        F  = npyscreen.Form(name = "ER-1 x-nucleo",)
#        #t  = F.add(npyscreen.TitleText, name = "Text:",)
#        #fn = F.add(npyscreen.TitleFilename, name = "Filename:")
#        #fn2 = F.add(npyscreen.TitleFilenameCombo, name="Filename2:")
#        #dt = F.add(npyscreen.TitleDateCombo, name = "Date:")
#        #s  = F.add(npyscreen.TitleSlider, out_of=12, name = "Slider")
#        #ml = F.add(npyscreen.MultiLineEdit,
#        #       value ="" """try typing here!\nMutiline text, press ^R to reformat.\n""",
#        #       max_height=5, rely=9)
#        ms = F.add(npyscreen.TitleSelectOne, max_height=4, value = [1,], name="Propeller Port",
#                values = self.ports if self.ports else ["<None Found>"], scroll_exit=True)
#        ms2= F.add(npyscreen.TitleMultiSelect, max_height =-2, value = [1,], name="Enable",
#                values = ["Joystick"], scroll_exit=True)
#
#        # This lets the user interact with the Form.
#        F.edit()
#
#        print(ms.get_selected_objects())
class Options_Form(npyscreen.Form):
    def create(self):
        self.name = self.add(npyscreen.TitleText, name='Name')
        self.serialPort = self.add(npyscreen.TitleSelectOne, max_height=4, value=[1,], name="Propeller Port")
        self.joyStick= self.add(npyscreen.TitleMultiSelect, max_height =-2, value = [1,], name="Enable",
                values = ["Joystick"], scroll_exit=True)
        self.edit()

    def afterEditing(self):
        print "Editing done. %s  %s" %(self.serialPort.get_value(), self.joyStick.get_value())
        self.parentApp.setNextForm(None)

class Controller_Application(npyscreen.NPSAppManaged):
    port = None
    def onStart(self):
        pt = PortTools()
        self.ports = pt.get_ports()
        self.addForm('MAIN', Options_Form, name='Options')
        
    def onCleanExit(self):
        if self.port:
            self.port.close()

if __name__ == "__main__":
    App = Controller_Application().run()
    
