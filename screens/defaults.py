from templates import TemplateScreen, SpecialCommandCatcher, ScreenDoneException, QuitException, DecorationScreen
import gamepackage

class BaseScreen(TemplateScreen):
    def trigger_specials(self):
        specialscreen = DefaultSpecials(self.controller)
        self.controller.add_screen(specialscreen)

class DefaultMenu(BaseScreen):
    def __init__(self, controller):
        BaseScreen.__init__(self, controller)
        self.dissapear_on_quit = True
    def __repr__(self):
        return "Main Menu"

    def trigger_specials(self):
        specials = MainMenuSpecials(self.controller)
        self.controller.add_screen(specials)

    def set_state(self):
        self.clear_state()
        self.clear_triggers()
        self.state('Main Menu', center=2)
        if len(self.controller.screen_queue)>1:
            self.add_trigger('r', 1)
            self.state("(r)Resume Game", indent=1)
        self.add_trigger('n', 2)
        self.state("(n)New Game", indent=1)
        savefile_list = gamepackage.saves.get_savefile_list()
        savefile_str = self.controller.savefile_str
        if savefile_str:
            expanded = gamepackage.saves.expand_savefile_name(savefile_str)
            savefile_list = [x for x in savefile_list if not x in (savefile_str,expanded)]
        if savefile_list:
            self.add_trigger('l', 3)
            if savefile_str:
                self.state("(l)Load another saved game", indent=1)
            else:
                self.state("(l)Load a saved game", indent=1)
        self.add_trigger('u', 4)
        self.state('(u)Change UI', indent=1)
        self.add_trigger('q', 5)
        self.state('(q)Quit game', indent=1)

    def execute_trigger(self, trigger):
        if trigger == 1:
            raise ScreenDoneException
        elif trigger == 2:
            self.controller.load_save(new=True)
        elif trigger == 3:
            pass
        elif trigger == 4:
            pass
        elif trigger == 5:
            self.die()
            raise QuitException

class DefaultSpecials(SpecialCommandCatcher):
    def __init__(self, controller):
        specials = {'quit\n':1, 'file\n':2, 'ui\n':3, 'refresh\n':4, 'menu\n':5}
        SpecialCommandCatcher.__init__(self, controller, specials)
        self.helpstr = "Valid special options: "+' '.join(['#'+x.strip() for x in sorted(self.specials)])
    def execute_special(self, trigger):
        if trigger == 1:
            self.die()
            raise QuitException
        elif trigger == 2:
            self.display('Current save file: %s'%self.controller.savefile_str)
        elif trigger == 3:
            self.display('Current ui module: %s'%self.controller.ui.ui_str)
        elif trigger == 4:
            self.full_display()
        elif trigger == 5:
            mainmenu = DefaultMenu(self.controller)
            self.after_me_goto(mainmenu)
    def __repr__(self):
        return "Special Action Menu"

class MainMenuSpecials(DefaultSpecials):
    def __init__(self, controller):
        specials = {'quit\n':1, 'file\n':2, 'ui\n':3, 'refresh\n':4}
        SpecialCommandCatcher.__init__(self, controller, specials)
        f = lambda x: '#'+x.strip() if x != 'menu' else '(#menu)'
        self.helpstr = "Valid special options: "+' '.join([f(x) for x in sorted(self.specials.keys()+['menu'])]) 

    def fail_message(self, event_str):
        if event_str and event_str == 'menu':
            self.display("You are already at the main menu!")
        else:
            DefaultSpecials.fail_message(self, event_str)

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
