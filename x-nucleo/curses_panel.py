#!/usr/bin/env python2                                                       

import curses                                                                
from curses import panel   

def make_box(h,l, y,x, str):
    win = curses.newwin(h,l, y,x)
    win.erase()
    win.box()
    win.addstr(2, 2, str)
    pan = curses.panel.new_panel(win)
    return win, pan

def make_panel(stdscreen):
    window = stdscreen.subwin(0,0)                                  
    window.keypad(1)                                                
    pan = panel.new_panel(window)                            
    #print "created pan" , pan
    pan.hide()                                                    
    panel.update_panels()  
    return window, pan
class Menu(object):                                                          

    def __init__(self, items, stdscreen):                                    
        
        self.window, self.panel = make_panel(stdscreen)

        self.position = 0                                                    
        self.items = items                                                   
        self.items.append(('exit','exit'))                                   

    def navigate(self, n):                                                   
        self.position += n                                                   
        if self.position < 0:                                                
            self.position = 0                                                
        elif self.position >= len(self.items):                               
            self.position = len(self.items)-1                                

    def display(self):                                                       
        self.panel.top()                                                     
        self.panel.show()                                                    
        self.window.clear()                                                  
        print "main menu display..."
        while True:                                                          
            self.window.refresh()                                            
            curses.doupdate()                                                
            for index, item in enumerate(self.items):                        
                if index == self.position:                                   
                    mode = curses.A_REVERSE                                  
                else:                                                        
                    mode = curses.A_NORMAL                                   

                msg = '%d. %s' % (index, item[0])                            
                self.window.addstr(1+index, 1, msg, mode)                    

            key = self.window.getch()                                        

            if key in [curses.KEY_ENTER, ord('\n')]: 
                #print "Got Curses KEY_ENTER"                        
                if self.position == len(self.items)-1:                       
                    break                                                    
                else:                                                        
                    self.items[self.position][1]()                           

            elif key == curses.KEY_UP:
                #print "Got Curses KEY_UP"                                         
                self.navigate(-1)                                            

            elif key == curses.KEY_DOWN:
                #print "Got Curses KEY_DOWN"                                       
                self.navigate(1)                                             

        self.window.clear()                                                  
        self.panel.hide()                                                    
        panel.update_panels()                                                
        curses.doupdate()

class Box(object):
    highlightText = None
    normalText = None
    def __init__(self, stdscreen):   
        self.window, self.panel = make_box(21, 110, 1, 20, "")
        #self.window.addstr(1,1,"", self.highlightText)                              
        self.window.refresh()

    def display(self, items):
        highlightText = curses.color_pair(1)
        normalText = curses.A_NORMAL
        position = 1
        row_num = len(items)
        for i in range(1,len(items) + 1):
            if not items:
                self.window.addstr(1,1,"There aren't strings", highlightText)
            else:
                if (i == position):
                    self.window.addstr(i,2,items[i-1], highlightText)
                else:
                    self.window.addstr(i,2,items[i-1], normalText)
                if i == row_num:
                    break
        self.window.refresh()
    

class MyApp(object):                                                         

    def __init__(self, stdscreen):                                           
        self.screen = stdscreen    
        self.screen.border(0)  
        curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_CYAN)                                                
        curses.curs_set(0)     
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        self.screen.keypad(1)                                              

        submenu_items = [                                                    
                ('data', self.view_data),                                       
                ('flash', curses.flash)                                      
                ]                                                            
        submenu = Menu(submenu_items, self.screen)                           

        main_menu_items = [                                                  
                ('show', submenu.display),                                       
                ('flash', curses.flash),                                     
                ('submenu', submenu.display)                                 
                ]               
        #controller_mem = Box(stdscreen)                                            
        #controller_mem.display(["Driver memory values..."])                                             
        main_menu = Menu(main_menu_items, self.screen)                       
        main_menu.display()      
    def view_data(self):
        window, box =  make_box(20, 80, 10, 2, "initial text")
        window.refresh()

if __name__ == '__main__':                                                       
    curses.wrapper(MyApp)   
