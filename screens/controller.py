import sys
import gamepackage
from screens.templates import ScreenDoneException, QuitException, CloseMenusException
from screens.defaults import DefaultMenu, MainDeco

class ScreenController(object):
    def __init__(self, ui_str=None, savefile_str=None, new=False):
        self.current_screen = None
        self.ui = None
        if not ui_str: ui_str = 'basic'
        self.load_ui(ui_str)
        self.screen_queue = []
        self.menu_queue = []
        self.savefile_str = None
        if new or savefile_str:
            self.load_save(savefile_str, new)
    def last_usage_info(self):
        return (self.savefile_str, self.ui.ui_str)

    def load_save(self, savefile_str=None, new=False):
        if self.savefile_str: self.save_game()
        if new:
            savefile_str = gamepackage.saves.get_new_savename()
            game_screen = gamepackage.new_game()
            deco_screen = MainDeco()
            screen_q = [deco_screen]
        else:
            game_screen , screen_q= gamepackage.saves.get_savedgame(savefile_str)
        self.savefile_str = savefile_str
        if new:
            self.display('Creating save file %s...'%self.savefile_str)
        else:
            self.display('Loading save file %s...'%self.savefile_str)
        self.screen_queue = screen_q
        self.menu_queue = []
        self.select_screen(game_screen)

    def save_game(self, **kwargs):
        if 'quitting' in kwargs:
            self.real_display('Saving game in file %s...'%self.savefile_str)
        else:
            self.display('Saving game in file %s...'%self.savefile_str)
        gamepackage.saves.save_game(self)

    def stack_screen(self, screen):
        if screen.is_menu:
            self.menu_queue.append(screen)
        else:
            self.screen_queue.append(screen)
    def add_screen(self, screen):
        if self.current_screen: self.stack_screen(self.current_screen)
        self.select_screen(screen)
    def select_screen(self, screen, **kwargs):
        self.current_screen = screen
        if screen and not kwargs.get('norefresh', False):
            screen.display_flag = True

    def next_screen(self, **kwargs):
        if self.menu_queue:
            self.select_screen(self.menu_queue.pop(), **kwargs)
        elif self.screen_queue:
            self.select_screen(self.screen_queue.pop(), **kwargs)
        else:
            self.select_screen(None)
            self.savefile_str = None
            deco_screen = MainDeco()
            self.add_screen(deco_screen)
            next_screen = DefaultMenu()
            self.add_screen(next_screen)

    def load_ui(self, ui_str):
        if self.ui:
            backup_queue = self.ui.event_queue
        else:
            backup_queue = None
        self.ui = getattr(sys.modules['uimodules.'+ui_str], 'UI')()
        if backup_queue: self.ui.event_queue = backup_queue
        self.ui.ui_str = ui_str
        self.display("UI '%s' loaded..."%ui_str)
    def get_event(self):
        return self.ui.get_event()
    def put_event_back(self, event):
        self.ui.put_event_back(event)
    def display(self, text, **kwargs):
        if self.current_screen:
            self.current_screen.display(text, **kwargs)
        else:
            self.real_display(text, **kwargs)
    def real_display(self, text, **kwargs):
        self.ui.display(text, **kwargs)
    def temp_display(self, screen):
        for text, kwargs in screen.temp_display_list:
            self.real_display(text, **kwargs)
        screen.temp_display_list = []
    def full_display(self):
        display_bubbles = {}
        for screen in reversed(self.screen_queue+self.menu_queue+[self.current_screen]):
            if screen.no_display: continue
            for num, stuff in screen.bubbles.items():
                if num in display_bubbles: continue
                else:
                    display_bubbles[num] = stuff
        for num, stuff in sorted(display_bubbles.items()):
            for line, arg_dict in stuff:
                self.real_display(line, **arg_dict)

    def run(self):
        if not self.current_screen:
            self.next_screen()
        else:
            screen = self.current_screen
            try:
                screen.run(self)
            except ScreenDoneException as e:
                if e.uimodule:
                    self.load_ui(e.uimodule)
                if e.die:
                    self.next_screen(norefresh=e.norefresh)
                if e.savefile == 'new':
                    self.load_save(new=True)
                elif e.savefile: 
                    self.load_save(e.savefile)
                if e.next_screen:
                    self.add_screen(e.next_screen)
            except CloseMenusException as e:
                self.menu_queue = []
                if self.current_screen.is_menu: self.current_screen = None
                if e.then_open == 'main':
                    self.add_screen(DefaultMenu())
                elif e.then_open:
                    self.add_screen(e.then_open)
            finally:
                self.temp_display(screen)

    def run_loop(self):
        self.real_display("Starting game...")
        try:
            while True:
                self.run()
        except QuitException: pass
        finally:
            if self.savefile_str: self.save_game(quitting=True)
            self.real_display("Goodbye", center=2)
            self.real_display("")

