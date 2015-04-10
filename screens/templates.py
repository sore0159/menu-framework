import gamepackage
import sys
from collections import deque

class ScreenDoneException(Exception): pass
class QuitException(Exception):pass

class ScreenController(object):
    def __init__(self, ui_str=None, savefile_str=None, new=False):
        if not ui_str: ui_str = 'basic'
        self.load_ui(ui_str)
        self.screen_queue = deque()
        self.current_screen = None
        if new or savefile_str:
            self.load_save(savefile_str, new)
        else:
            next_screen = DefaultScreen(self)
            self.new_screen(next_screen)

    def last_usage_info(self):
        return (self.savefile_str, self.ui.ui_str)

    def load_save(self, savefile_str=None, new=False):
        if new:
            savefile_str, game_screen, screen_q = gamepackage.saves.new_game(self)
        else:
            game_screen , screen_q= gamepackage.saves.load_savefile(self, savefile_str)
        self.savefile_str = savefile_str
        self.current_screen = game_screen
        self.screen_queue = deque(screen_q)

    def save_state(self):
        self.gamepackage.saves.save_state(self, self.savefile_str)

    def new_screen(self, screen):
        if self.current_screen: self.screen_queue.append(self.current_screen)
        self.current_screen = screen
    def next_screen(self):
        try:
            self.current_screen = self.screen_queue.pop()
        except IndexError:
            raise QuitException
    def load_ui(self, ui_str):
        self.ui = getattr(sys.modules['uimodules.'+ui_str], 'UI')()
        self.ui.ui_str = ui_str
    def get_event(self):
        return self.ui.get_event()
    def display(self, text, **kwargs):
        self.ui.display(text, **kwargs)
    def run(self):
        self.display("Hello", center=1)
        try:
            while True:
                try:
                    self.current_screen.run()
                except ScreenDoneException:
                    self.next_screen()
        except QuitException: pass
        finally:
            self.quit()
    def quit(self):
        self.display("Goodbye", center=1)
        self.display("")

class DefaultScreen(object):
    def __init__(self, controller):
        self.controller = controller
        self.previous_screen = controller.current_screen
        self.set_state()
    def set_state(self):
        self.state_list = []
    def state(self, text, **kwargs):
        self.state_list.append((text, kwargs))
    def get_event(self):
        return self.controller.get_event()
    def display(self, text, **kwargs):
        self.controller.display(text, **kwargs)
    def new_screen(self, screen):
        self.controller.new_screen(screen)
    def run(self):
        for line, arg_dict in self.state_list:
            self.display(line, **arg_dict)
        event = self.get_event()
        self.display('EVENT: %s'%event)

class DepthScreen(DefaultScreen):
    def set_state(self):
        temp_depth = (len(self.controller.screen_queue)+1)
        if self.controller.current_screen: temp_depth+=1
        self.state = 'DEPTH:%s'%temp_depth+'\n%s'%self.controller.file_data
        self.num_events = 0
        self.while_gone = 0

    def missed_event(self):
        self.while_gone +=1
        if self.previous_screen:
            self.previous_screen.missed_event()
    def get_event(self):
        self.num_events +=1
        if self.previous_screen:
            self.previous_screen.missed_event()
        return self.controller.get_event()
    def run(self):
        self.display(self.state, center=2)
        if self.while_gone:
            self.display('%s EVENTS WHILE GONE'%self.while_gone)
            self.while_gone = 0
        event = self.get_event()
        self.display('EVENT #%s: %s'%(self.num_events, event))
        if event == 'n':
            self.new_screen(DefaultScreen(self.controller))
            return
        elif event == 'q':
            raise ScreenDoneException

