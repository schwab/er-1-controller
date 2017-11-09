#!/usr/bin/env python

import curses
import curses.textpad
import time

stdscr = curses.initscr()

#curses.noecho()
#curses.echo()
stdscr.border(0)
stdscr.addstr(12, 25, "Python curses in action ! ")
global screen
screen = stdscr.subwin(23, 79, 0, 0)
screen.box()
screen.hline(2, 1, curses.ACS_HLINE, 77)
screen.refresh()
stdscr.refresh()
stdscr.getch()



#begin_x = 20
#begin_y = 7
#height = 5
#width = 40
#win = curses.newwin(height, width, begin_y, begin_x)
#tb = curses.textpad.Textbox(win)
#text = tb.edit()
#curses.addstr(4,1,text.encode('utf_8'))

#hw = "Hello world!"
#while 1:
#    c = stdscr.getch()
#    if c == ord('p'): 
#    elif c == ord('q'): break # Exit the while()
#    elif c == curses.KEY_HOME: x = y = 0

curses.endwin()
