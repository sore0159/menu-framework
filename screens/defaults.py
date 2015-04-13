from templates import ScreenDoneException, QuitException, DecorationScreen, CloseMenusException, BaseScreen, DefaultSpecials
import gamepackage, uimodules

class UIMenu(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
        self.name = "UI Menu"

    def get_controller_info(self, controller):
        '''DO NOT STORE LINKS'''
        info = self.controller_info
        info['cur_game'] = len(controller.screen_queue)>1
        info['menu_q'] = len(controller.menu_queue)
        info['cur_ui'] = controller.ui.ui_str

    def set_state(self):
        self.clear_state()
        self.clear_triggers()
        self.state('UI Menu', center=2)
        info = self.controller_info
        if info['cur_game']:
            self.add_trigger('r', 1)
            self.state("(r)Resume Current Game", indent=1)
        if info['menu_q']:
            self.add_trigger('m', 2)
            self.state("(m)Back to Previous Menu", indent=1)
        cur_ui = info['cur_ui']
        other_uis = [x for x in uimodules.mod_list if x != cur_ui]
        other_uis.sort()
        self.ui_choices = other_uis
        self.state("You are currently using the '%s' UI."%cur_ui)
        if not other_uis:
            self.state('No alternate UIs available!', indent=1)
        else:
            self.state("Load alternate UI module:")
            for i,ui in enumerate(other_uis):
                self.state('(%s) %s'%(i, ui), indent=1)
                self.add_trigger('%s'%i, i+3)

    def execute_trigger(self, trigger):
        if trigger == 1:
            raise CloseMenusException
        elif trigger == 2:
            raise ScreenDoneException
        else:
            ui_str = self.ui_choices[trigger-3]
            self.display_flag = True
            raise ScreenDoneException(die=False, uimodule=ui_str)

class SaveMenu(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
        self.name = "Saves Menu"

    def get_controller_info(self, controller):
        '''DO NOT STORE LINKS'''
        info = self.controller_info
        info['cur_game'] = len(controller.screen_queue)>1
        info['menu_q'] = len(controller.menu_queue)
        info['cur_save'] = controller.savefile_str

    def set_state(self):
        self.clear_state()
        self.clear_triggers()
        self.state('Saved Game Menu', center=2)
        info = self.controller_info
        if info['cur_game']:
            self.add_trigger('r', 1)
            self.state("(r)Resume Current Game", indent=1)
        if info['menu_q']:
            self.add_trigger('m', 2)
            self.state("(m)Back to Previous Menu", indent=1)
        savefile_list = gamepackage.saves.get_savefile_list()
        savefile_str = info['cur_save']
        savefile_list = [x for x in savefile_list if x != savefile_str and x[-4:] != '.pkl']
        savefile_list.sort()
        self.save_choices = savefile_list
        if savefile_list:
            if savefile_str:
                self.state("Currently playing: %s"%savefile_str)
                self.state("Save current game and load:")
            else:
                self.state("Load saved game:")
            for i, save_str in enumerate(savefile_list):
                self.state("(%d) %s"%(i, save_str), indent=1)
                self.add_trigger('%d'%i, 3+i)
        else:
            self.state("No saved games available to load!", indent=1)

    def execute_trigger(self, trigger):
        if trigger == 1:
            raise CloseMenusException
        elif trigger == 2:
            raise ScreenDoneException
        else:
            save_str = self.save_choices[trigger-3]
            raise ScreenDoneException(savefile=save_str)

class DefaultMenu(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
        self.name = "Main Menu"

    def trigger_specials(self):
        specials = MainMenuSpecials()
        raise ScreenDoneException(die=False, next_screen=specials)

    def get_controller_info(self, controller):
        '''DO NOT STORE LINKS'''
        info = self.controller_info
        info['cur_game'] = len(controller.screen_queue)>1
        info['cur_save'] = controller.savefile_str

    def set_state(self):
        self.clear_state()
        self.clear_triggers()
        self.state('Main Menu', center=2)
        info = self.controller_info
        if info['cur_game']:
            self.add_trigger('r', 1)
            self.state("(r)Resume Game", indent=1)
        self.add_trigger('n', 2)
        self.state("(n)New Game", indent=1)
        savefile_list = gamepackage.saves.get_savefile_list()
        savefile_str = info['cur_save']
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
            raise CloseMenusException
        elif trigger == 2:
            raise ScreenDoneException(savefile='new')
        elif trigger == 3:
            savemenu = SaveMenu()
            raise ScreenDoneException(die=False, next_screen=savemenu)
        elif trigger == 4:
            uimenu = UIMenu()
            raise ScreenDoneException(die=False, next_screen=uimenu)
        elif trigger == 5:
            raise QuitException

class MainMenuSpecials(DefaultSpecials):
    def __init__(self):
        DefaultSpecials.__init__(self)
        self.name = "Main Menu Specials"
        self.event_triggers.pop('menu')
        self.helpstr = self.helpstr.replace('#menu', '(#menu)')

    def fail_message(self, event_str):
        if event_str and event_str == 'menu':
            self.display("You are already at the main menu!")
        else:
            DefaultSpecials.fail_message(self, event_str)

class MainDeco(DecorationScreen):
    def __init__(self):
        DecorationScreen.__init__(self)
        self.name = "Main Border"
        self.clear_state(bubble=0)
        self.state('Python UI Framework', center=1, bubble=0)
        self.clear_state(bubble=10)
        self.state('', bubble=10)
        self.state('', divider=1, bubble=10)





