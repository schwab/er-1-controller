from __future__ import division  #You don't need this in Python3
import curses
from math import *

screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
screen.keypad(1)
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_CYAN)
highlightText = curses.color_pair(1)
normalText = curses.A_NORMAL
screen.border(0)
curses.curs_set(0)
reg_box = curses.newwin(12,64,1,1)
reg_box.box()


strings = ["a","b","c","d","e","f","g","h","i","l","m","n"]
box_rows = 10

pages = int(ceil(row_num/box_rows))
position = 1
page = 1


screen.refresh()
reg_box.refresh()

def box_add_items(box, items, max_row):
    highlightText = curses.color_pair(1)
    normalText = curses.A_NORMAL
    row_num = len(strings)
    for i in range(1,max_row + 1):
        if row_num == 0:
            box.addstr(1,1,"There aren't strings", highlightText)
        else:
            if (i == position):
                box.addstr(i,2,items[i-1], highlightText)
            else:
                box.addstr(i,2,items[i-1], normalText)
            if i == row_num:
                break

def key_scroll_screen(scr, box):
    
    x = scr.getch()
    while x != 27:
        if (x == curses.KEY_DOWN):
            if page == 1:
                if position < i:
                    position = position + 1
                else:
                    if pages > 1:
                        page = page +1
                        position = 1 + (box_rows * (page - 1))
            elif page == pages:
                if position < row_num:
                    position = position + 1
            else:
                if position < box_rows+(box_rows*(page-1)):
                    position = position + 1
                else:
                    page = page + 1
                    position = 1 + (box_rows * (page - 1))
        if (x == curses.KEY_UP):
            if page == 1:
                if position > 1:
                    position = position - 1
            else:
                if position > (1 + (box_rows*(page-1))):
                    position = position - 1
                else:
                    page = page - 1
                    position = box_rows + (box_rows * (page - 1))
        if (x == curses.KEY_LEFT):
            if page > 1:
                page = page - 1
                position = 1 + (box_rows * (page - 1))

        if (x == curses.KEY_RIGHT):
            if page < pages:
                page = page + 1
                position = (1 + (box_rows * (page - 1)))


        box.erase()
        scr.border(0)
        box.border(0)

        for i in range(1+(box_rows*(page-1)),box_rows+1+(box_rows*(page-1))):
            if row_num == 0:
                box.addstr(1,1,"There aren't strings", highlightText)
            else:

                if (i+(box_rows*(page-1)) == position+(box_rows*(page-1))):
                    box.addstr(i-(box_rows*(page-1)),2,strings[i-1], highlightText)
                else:

                    box.addstr(i-(box_rows*(page-1)),2,strings[i-1],normalText)
                if i == row_num:
                    break



        scr.refresh()
        box.refresh()
        x = scr.getch()
try:
    box_add_items(reg_box, strings, box_rows)
    key_scroll_screen(screen, reg_box)
except KeyboardInterrupt as err:
    curses.endwin()
    exit()