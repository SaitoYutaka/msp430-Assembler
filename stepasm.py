import random, string, traceback
import curses

class StepAssemble(object):
    def __init__(self, scr, char=ord('*'), ainfo=[]):
        self.state = {}
        self.scr = scr
        Y, X = self.scr.getmaxyx()
        self.X, self.Y = X-2, Y-2-1
        self.char = char
        self.scr.clear()
        self.SOURCE,self.LABEL,self.L_ADDRESS,self.ADDRESS,self.OPCODE = range(5)
        self.ainfo = ainfo

        self.posx = 1
        self.lineno = 0

        head_line = 'source                    address  machine code           note'

        curses.init_pair(4, curses.COLOR_GREEN, 0)
        curses.init_pair(5, curses.COLOR_RED, 0)
        self.scr.attrset(curses.color_pair(5))
        self.scr.addstr(0, 0, head_line)

        n = 1
        for s in self.ainfo:
             self.scr.addstr(n, 0, s[0])
             n += 1

        self.scr.refresh()

    def next(self):
        if len(self.ainfo) <= self.lineno:return
        if '.org' in self.ainfo[self.lineno][self.SOURCE]:
            # note
            self.scr.attrset(curses.color_pair(4))
            self.scr.addstr(self.posx, 58, '; Set origin address')
        elif self.ainfo[self.lineno][self.SOURCE][-1] == ':':
            self.scr.attrset(curses.color_pair(4))
            self.scr.addstr(self.posx, 58, '; Address:'+ '0x'+'{0:04x}'.format(self.ainfo[self.lineno][self.L_ADDRESS]))
        elif self.ainfo[self.lineno][self.ADDRESS] != '':
            self.scr.attrset(curses.color_pair(5))
            # address
            self.scr.addstr(self.posx, 26, '{0:#x}'.format(self.ainfo[self.lineno][self.ADDRESS]))

            # machine code
            n = 0
            for x in self.ainfo[self.lineno][self.OPCODE]:
                self.scr.addstr(self.posx, 35 + n, '0x'+'{0:04x}'.format(x))
                n += 7
        self.scr.refresh()
        self.lineno += 1
        self.posx += 1

    def prev(self):
        if self.posx != 1:
            self.lineno -= 1
            self.posx -= 1
        self.scr.addstr(self.posx, 26, ' '*60)
        self.scr.refresh()

def erase_menu(stdscr, menu_y):
    "Clear the space where the menu resides"
    stdscr.move(menu_y, 0)
    stdscr.clrtoeol()
    stdscr.move(menu_y+1, 0)
    stdscr.clrtoeol()

def display_menu(stdscr, menu_y):
    "Display the menu of possible keystroke commands"
    erase_menu(stdscr, menu_y)
    stdscr.addstr(menu_y+1, 4,
                  'Right)Prev, Left)Next, Q)uit')

def keyloop(stdscr,asminfo):
    # Clear the screen and display the menu of keys
    stdscr.clear()
    stdscr_y, stdscr_x = stdscr.getmaxyx()
    menu_y = (stdscr_y-3)-1
    display_menu(stdscr, menu_y)

    # Allocate a subwindow for the Life board and create the board object
    subwin = stdscr.subwin(stdscr_y-3, stdscr_x, 0, 0)
    stepasm = StepAssemble(subwin, char=ord('*'), ainfo = asminfo)

    # xpos, ypos are the cursor's position
    xpos, ypos = stepasm.X//2, stepasm.Y//2

    # Main loop:
    while (1):

        c = stdscr.getch()                # Get a keystroke
        if 0<c<256:
            c = chr(c)
            if c in 'Qq':
                break
            else: pass                  # Ignore incorrect keys
        elif c == curses.KEY_LEFT:
            stepasm.prev()
        elif c == curses.KEY_RIGHT:
            stepasm.next()
        else:
            # Ignore incorrect keys
            pass


def main(stdscr,asminfo):
    keyloop(stdscr,asminfo)                    # Enter the main loop

def stepasm(asminfo):
    curses.wrapper(main,asminfo)

if __name__ == '__main__':
    curses.wrapper(main)
