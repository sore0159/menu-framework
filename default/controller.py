import sys
import gamepackage
from screens.templates import ScreenDoneException, QuitException, DefaultMenu, DecorationScreen

class MainDeco(DecorationScreen):
    def __init__(self, controller):
        DecorationScreen.__init__(self, controller)
        self.clear_state(bubble=0)
        self.state('Gorilla Island', center=1, bubble=0)
        self.clear_state(bubble=10)
        self.state('', bubble=10)
        self.state('', divider=1, bubble=10)
    def __repr__(self):
        return "Main Border"

class ScreenController(object):
    def __init__(self, ui_str=None, savefile_str=None, new=False):
        if not ui_str: ui_str = 'basic'
        self.load_ui(ui_str)
        self.screen_queue = []
        self.current_screen = None
        self.savefile_str = None
        if new or savefile_str:
            self.load_save(savefile_str, new)
    def last_usage_info(self):
        return (self.savefile_str, self.ui.ui_str)

    def load_save(self, savefile_str=None, new=False):
        if self.savefile_str: self.save_game()
        if new:
            savefile_str = gamepackage.saves.get_new_savename()
            game_screen = gamepackage.new_game(self)
            deco_screen = MainDeco(self)
            screen_q = [deco_screen]
        else:
            game_screen , screen_q= gamepackage.saves.get_savedgame(savefile_str)
        self.savefile_str = savefile_str
        if new:
            self.display('Creating save file %s...'%self.savefile_str)
        else:
            self.display('Loading save file %s...'%self.savefile_str)
        self.screen_queue = [self.control(x) for x in screen_q]
        self.select_screen(self.control(game_screen))

    def control(self, screen):
        screen.controller = self
        return screen

    def save_game(self):
        self.display('Saving game in file %s...'%self.savefile_str)
        gamepackage.saves.save_game(self)

    def select_screen(self, screen, **kwargs):
        self.current_screen = screen
        if 'norefresh' not in kwargs:
            screen.display_flag = True

    def add_screen(self, screen):
        if self.current_screen: 
            self.screen_queue.append(self.current_screen)
        self.select_screen(screen)

    def next_screen(self, **kwargs):
        try:
            self.select_screen(self.screen_queue.pop(), **kwargs)
        except IndexError:
            self.select_screen(None)
            self.savefile_str = None
            deco_screen = MainDeco(self)
            self.add_screen(deco_screen)
            next_screen = DefaultMenu(self)
            self.add_screen(next_screen)

    def load_ui(self, ui_str):
        self.ui = getattr(sys.modules['uimodules.'+ui_str], 'UI')()
        self.ui.ui_str = ui_str
        self.display("UI '%s' loaded..."%ui_str)
    def get_event(self):
        return self.ui.get_event()
    def passed_event(self, event):
        return False
    def display(self, text, **kwargs):
        self.ui.display(text, **kwargs)
    def full_display(self):
        display_bubbles = {}
        for screen in reversed(self.screen_queue+[self.current_screen]):
            if screen.no_display: continue
            for num, stuff in screen.bubbles.items():
                if num in display_bubbles: continue
                else:
                    display_bubbles[num] = stuff
        for num, stuff in sorted(display_bubbles.items()):
            for line, arg_dict in stuff:
                self.display(line, **arg_dict)


    def run(self):
        if not self.current_screen:
            self.next_screen()
        else:
            try:
                self.current_screen.run()
            except ScreenDoneException:
                self.next_screen()

    def run_loop(self):
        self.display("Starting game...")
        try:
            while True:
                self.run()
        except QuitException: pass
        finally:
            self.quit()

    def quit(self):
        if self.savefile_str:
            self.save_game()
        self.display("Goodbye", center=2)
        self.display("")
