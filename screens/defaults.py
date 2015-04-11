from templates import TemplateScreen, SpecialCommandCatcher, ScreenDoneException, QuitException, DecorationScreen
import gamepackage, uimodules

class BaseScreen(TemplateScreen):
    def trigger_specials(self, controller):
        specialscreen = DefaultSpecials(controller)
        controller.add_screen(specialscreen)

class UIMenu(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
    def __repr__(self):
        return "UI Menu"

    def set_state(self, controller):
        self.clear_state()
        self.clear_triggers()
        self.state('UI Menu', center=2)
        if len(controller.screen_queue)>1:
            self.add_trigger('r', 1)
            self.state("(r)Resume Current Game", indent=1)
        if controller.menu_queue:
            self.add_trigger('m', 2)
            self.state("(m)Back to Previous Menu", indent=1)
        cur_ui = controller.ui.ui_str
        other_uis = [x for x in uimodules.mod_list if x != cur_ui]
        other_uis.sort()
        self.ui_choices = other_uis
        self.state("You are currently using the '%s' UI."%cur_ui)
        if not other_uis:
            self.state('No alternate UIs available!', indent=1)
        else:
            self.state("Load alternate UI module:")
            for i,ui in enumerate(other_uis):
                self.state('(l%s) %s'%(i, ui), indent=1)
                self.add_trigger('l%s'%i, i+3)

    def execute_trigger(self, controller, trigger):
        if trigger == 1:
            controller.resume_game()
            raise ScreenDoneException
        elif trigger == 2:
            raise ScreenDoneException
        else:
            ui_str = self.ui_choices[trigger-3]
            controller.load_ui(ui_str)
            self.display_flag = True

class SaveMenu(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
    def __repr__(self):
        return "Saves Menu"

    def set_state(self, controller):
        self.clear_state()
        self.clear_triggers()
        self.state('Saved Game Menu', center=2)
        if len(controller.screen_queue)>1:
            self.add_trigger('r', 1)
            self.state("(r)Resume Current Game", indent=1)
        if controller.menu_queue:
            self.add_trigger('m', 2)
            self.state("(m)Back to Previous Menu", indent=1)
        savefile_list = gamepackage.saves.get_savefile_list()
        savefile_str = controller.savefile_str
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
                self.state("(l%d) %s"%(i+1, save_str), indent=1)
                self.add_trigger('l%d'%(i+1), 3+i)
        else:
            self.state("No saved games available to load!", indent=1)

    def execute_trigger(self, controller, trigger):
        if trigger == 1:
            controller.resume_game()
            raise ScreenDoneException
        elif trigger == 2:
            raise ScreenDoneException
        else:
            save_str = self.save_choices[trigger-3]
            controller.load_save(save_str)

class DefaultMenu(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
    def __repr__(self):
        return "Main Menu"

    def trigger_specials(self, controller):
        specials = MainMenuSpecials(controller)
        controller.add_screen(specials)

    def set_state(self, controller):
        self.clear_state()
        self.clear_triggers()
        self.state('Main Menu', center=2)
        if len(controller.screen_queue)>1:
            self.add_trigger('r', 1)
            self.state("(r)Resume Game", indent=1)
        self.add_trigger('n', 2)
        self.state("(n)New Game", indent=1)
        savefile_list = gamepackage.saves.get_savefile_list()
        savefile_str = controller.savefile_str
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

    def execute_trigger(self, controller, trigger):
        if trigger == 1:
            controller.resume_game()
            raise ScreenDoneException
        elif trigger == 2:
            controller.load_save(new=True)
        elif trigger == 3:
            savemenu = SaveMenu()
            controller.add_screen(savemenu)
        elif trigger == 4:
            uimenu = UIMenu()
            controller.add_screen(uimenu)
        elif trigger == 5:
            raise QuitException

class DefaultSpecials(SpecialCommandCatcher):
    def __init__(self, controller):
        specials = {'quit\n':1, 'file\n':2, 'ui\n':3, 'refresh\n':4, 'menu\n':5, 'help\n':6, 'resume\n':7}
        SpecialCommandCatcher.__init__(self, specials)
        self.helpstr = "Valid special options: "+' '.join(['#'+x.strip() for x in sorted(self.specials)])+'\nType #help to for full description'
        if not controller.current_screen.is_menu and not controller.menu_queue:
            self.specials.pop('resume\n')
            self.helpstr = self.helpstr.replace('#resume', '(#resume)')
    def execute_special(self, controller, trigger):
        if trigger == 1:
            raise QuitException
        elif trigger == 2:
            controller.display('Current save file: %s'%controller.savefile_str)
        elif trigger == 3:
            controller.display('Current ui module: %s'%controller.ui.ui_str)
        elif trigger == 4:
            controller.full_display()
        elif trigger == 5:
            mainmenu = DefaultMenu()
            controller.menu_queue = [mainmenu]
        elif trigger == 6:
            self.long_help_display(controller)
        elif trigger == 7:
            controller.resume_game()
            raise ScreenDoneException
    def fail_message(self, controller, event_str):
        if event_str and event_str == 'resume':
            controller.display("You are already in game!")
        else:
            SpecialCommandCatcher.fail_message(self, controller, event_str)
    def long_help_display(self, controller):
        long_help = '''Special commands:
#file       -- Display the current savegame file
#help       -- Display this information
#menu       -- Go to the Main Menu
#quit       -- Quit the game entirely (saving your progress)
#refresh    -- Redraw the screen (handy if lots of failed prompts are in your way)
#resume     -- Close all menus and return to the game in progress
#ui         -- Display the current active UI module'''
        controller.display(long_help)
    def __repr__(self):
        return "Special Action Menu"

class MainMenuSpecials(DefaultSpecials):
    def __init__(self, controller):
        DefaultSpecials.__init__(self, controller)
        self.specials.pop('menu\n')
        self.helpstr = self.helpstr.replace('#menu', '(#menu)')

    def fail_message(self, controller, event_str):
        if event_str and event_str == 'menu':
            controller.display("You are already at the main menu!")
        else:
            DefaultSpecials.fail_message(self, controller, event_str)

class MainDeco(DecorationScreen):
    def __init__(self):
        DecorationScreen.__init__(self)
        self.clear_state(bubble=0)
        self.state('Game Title Here', center=1, bubble=0)
        self.clear_state(bubble=10)
        self.state('', bubble=10)
        self.state('', divider=1, bubble=10)
    def __repr__(self):
        return "Main Border"
