from collections import deque
from screens.templates import QuitException, ScreenDoneException
from uimodules import basic
import curses
  ######  Required by Menus:  ######
# display(text, flag)
# query(choices, special_choices)

class UI(basic.UI):
    def __init__(self):
        basic.UI.__init__(self)
        self.ui_str = 'cursesui'
        ##### CURSES FOILED AGAIN #####
        self.main_window = curses.initscr()
        curses.cbreak()
        self.main_window.keypad(1)
        self.main_window.border(0)
        self.main_window.addstr("Curses UI Module Loaded...")
        self.main_window.refresh()

    def close(self, **kwargs):
        self.main_window.keypad(0)
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
            except KeyboardInterrupt:
                raise QuitException
            else:
                try:
                    return chr(user_event)
                except ValueError:
                    return '!'

