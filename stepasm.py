import random, string, traceback
import curses

class StepAssemble(object):
    def __init__(self, scr, ainfo=[]):

        self.scr = scr


        self.scr.clear()
        self.LINE, self.LINE_PREP, self.LINE_LABEL2SDDR, self.LABEL, self.LABEL_ADDR, self.ADDR, self.OPCODE = range(7)
        #self.SOURCE,self.LABEL,self.L_ADDRESS,self.ADDRESS,self.OPCODE = range(5)
        self.ainfo = ainfo

        self.posx = 1
        self.lineno = 0
        self.step = 0

        head_line = 'source                    address  machine code           note'

        curses.init_pair(4, curses.COLOR_GREEN, 0)
        curses.init_pair(5, curses.COLOR_RED, 0)
        self.scr.attrset(curses.color_pair(5))
        self.scr.addstr(0, 0, head_line)

        n = 1
        for s in self.ainfo:
             self.scr.addstr(n, 0, s[self.LINE])
             n += 1
        self.step = 1

        self.scr.refresh()

    def preprocess(self,step='next'):
        n = 1

        for s in self.ainfo:
            if s[self.LINE_PREP] != s[self.LINE]:
                if step=='next':
                    self.scr.attrset(curses.color_pair(4))
                    self.scr.addstr(n, 0, s[self.LINE_PREP]+'       ')
                else:
                    self.scr.attrset(curses.color_pair(5))
                    self.scr.addstr(n, 0, s[self.LINE]+'       ')
            n += 1
        self.scr.refresh()

    def label2addr(self):
        pass

    def isIncludeLABEL(self, line):
        if line[-1] == ':':return ''
        for label in self.ainfo:
            if label[self.LINE][-1] == ':':
                if label[self.LINE][:-1] in line:
                    return label[self.LINE]
        return ''

    def next(self):
        if self.step == 1:
            self.preprocess(step='next')
            self.step = 0
            return
        if len(self.ainfo) <= self.lineno:return

        if '.org' in self.ainfo[self.lineno][self.LINE]:
            # note
            self.scr.attrset(curses.color_pair(4))
            self.scr.addstr(self.posx, 58, '; Set origin address')

        elif self.isIncludeLABEL(self.ainfo[self.lineno][self.LINE]) != '':
            self.scr.attrset(curses.color_pair(5))
            self.scr.addstr(self.posx, 26, 'label')
            self.scr.refresh()

        elif self.ainfo[self.lineno][self.LINE][-1] == ':':
            self.scr.attrset(curses.color_pair(4))
            self.scr.addstr(self.posx, 58, '; Address:'+ '0x'+'{0:04x}'.format(self.ainfo[self.lineno][self.LABEL_ADDR]))
        elif self.ainfo[self.lineno][self.ADDR] != '':
            self.scr.attrset(curses.color_pair(5))
            # address
            self.scr.addstr(self.posx, 26, '{0:#x}'.format(self.ainfo[self.lineno][self.ADDR]))

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
        elif self.posx == 1:
            self.preprocess(step='prev')
            self.step = 1
            return
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
    stepasm = StepAssemble(subwin, ainfo = asminfo)

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
