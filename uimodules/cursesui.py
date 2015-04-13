from collections import deque
from screens.templates import QuitException, ScreenDoneException
from uimodules import basic
import curses
  ######  Required by Menus:  ######
# display(text, flag)
# query(choices, special_choices)

class UI(basic.UI):
    def __init__(self):
        self.ui_str = 'cursesui'
        self.left_padding = 4
        self.display_width = 70
        self.event_queue = deque()
        self.input_prompt = '\n>>> '
        self.char_dict = {1:'=', 2:'-', 3:' ', 4:'+'}
        ##### CURSES FOILED AGAIN #####
        self.main_window = curses.initscr()
        curses.cbreak()
        self.main_window.border(0)
        self.main_window.addstr("Curses UI Module Loaded...")
        self.main_window.refresh()

    def close(self, **kwargs):
        # add printing dump of cur screen contents when done
        curses.endwin()

    def display(self, text='', **kwargs):
        self.main_window.addstr( self.format_output(text, **kwargs)+'\n')

    def display_screen(self, lines):
        self.main_window.clear()
        self.main_window.addstr("\n\n\n")
        for text, kwargs in lines:
            self.display(text, **kwargs)
        self.main_window.refresh()

    def put_event_back(self, event):
        self.event_queue.append(event)

    def get_event(self):
        try:
            return self.event_queue.pop()
        except IndexError:
            try:
                user_event = self.main_window.getch()
            except (EOFError, KeyboardInterrupt):
                raise QuitException
            else:
                return chr(user_event)


