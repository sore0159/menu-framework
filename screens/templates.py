from collections import defaultdict
import gamepackage
class ScreenDoneException(Exception): pass
class QuitException(Exception):pass

class BaseScreen(object):
    def __init__(self, controller, default_bubble=1):
        self.default_specials = True
        self.no_display = False
        self.display_flag = True
        self.controller = controller
        self.previous_screen = controller.current_screen
        self.bubbles = {}
        self.default_bubble = default_bubble
        self.event_queue = []
        self.clear_triggers()
        self.set_state()
    def get_event(self):
        base_event = self.controller.get_event()
        event = base_event
        if self.default_specials: 
            if event == '#':
                self.event_queue = []
                self.trigger_default_specials()
                return 0
            elif event == '\n' and self.event_queue:
                self.event_queue = []
                self.display("Not a valid option: type # for special options")
        for char in ['']+self.event_queue:
            event+=char
            if event in self.event_triggers:
                self.event_queue = []
                self.event_display(event)
                return self.event_triggers[event]
        else:
            self.event_queue.append(base_event)
            pass_code = self.pass_event(base_event)
            return 0
    def event_display(self, event):
        self.display('\nExecuting command %s...'%event)
    def pass_event(self, event):
        if self.previous_screen:
            return self.previous_screen.passed_event(event)
        else:
            return self.controller.passed_event(event)
    def clear_triggers(self):
        self.event_triggers = {'#':'s'}
    def add_trigger(self, event_str, trigger_int):
        self.event_triggers[event_str] = trigger_int

    def display(self, text, **kwargs):
        self.controller.display(text, **kwargs)
    def clear_state(self, **kwargs):
        if 'bubble' in kwargs:
            bubble = kwargs.pop('bubble')
        else:
            bubble = self.default_bubble
        self.bubbles[bubble] = []
    def state(self, text, **kwargs):
        if 'bubble' in kwargs:
            bubble = kwargs.pop('bubble')
        else:
            bubble = self.default_bubble
        self.bubbles[bubble].append((text, kwargs))
    def full_display(self):
        self.controller.full_display()
    def die(self, **kwargs):
        '''For when you're done but don't want to raise a DoneExcept.
        For example, when you're a menu that's quitting, or if you need to pass args to next_screen'''
        self.controller.next_screen(**kwargs)
    def after_me_goto(self, screen):
        screen.previous_screen = self.previous_screen
        self.controller.screen_queue.append(screen)
    def trigger_default_specials(self):
        specials = DefaultSpecials(self.controller)
        self.controller.add_screen(specials)
    def run(self):
        if self.display_flag:
            self.full_display()
        trigger = self.get_event()
        if trigger: 
            self.display_flag = True
            self.execute_trigger(trigger)
        else: 
            self.display_flag = False

    ######### OVERLOAD ########
    def __repr__(self):
        return "Template Menu"
    def passed_event(self, event):
        return self.pass_event(event)
    def set_state(self):
        self.clear_state()
        self.state('Base Screen', center=1)
        self.add_trigger('q', 1)
        self.display_flag = True

    def execute_trigger(self, trigger):
        self.display('TRIGGER: %s'%trigger)
        self.display('EVENT QUEUE: '+''.join(self.event_queue))
        if trigger == 1: raise ScreenDoneException

class SpecialCommandCatcher(BaseScreen):
    def __init__(self, controller, special_dict):
        BaseScreen.__init__(self, controller)
        self.no_display = True
        self.specials = special_dict
        self.event_so_far = ''
        self.helpstr = "Valid special options: "+' '.join([x.strip() for x in self.specials])
    def get_event(self):
        base_event = self.controller.get_event()
        return base_event
    def set_state(self):pass
    def die(self):
        '''This is a small submenu, no display of its own'''
        self.controller.next_screen(norefresh=1)
    def run(self):
        event = self.get_event()
        self.event_so_far += event
        if self.event_so_far in self.specials:
            self.execute_special(self.specials[self.event_so_far])
            self.die()
        else:
            ev_len = len(self.event_so_far)
            if event == '\n' and self.event_so_far not in [x[:ev_len] for x in self.specials]:
                if self.event_so_far.strip():
                    self.display("'%s' is an invalid special option!"%self.event_so_far.strip())
                self.display(self.helpstr)
                self.die()
    ###### OVERLOAD #######
    def execute_special(self, trigger):
        pass

    def __repr__(self):
        return "Special Command Catcher"

class DefaultSpecials(SpecialCommandCatcher):
    def __init__(self, controller):
        specials = {'quit\n':1, 'file\n':2, 'ui\n':3, 'refresh\n':4, 'menu\n':5}
        SpecialCommandCatcher.__init__(self, controller, specials)
        self.helpstr = "Valid special options: "+' '.join(['#'+x.strip() for x in self.specials])
    def execute_special(self, trigger):
        if trigger == 1:
            self.die()
            raise QuitException
        elif trigger == 2:
            self.display('Current save file: %s'%self.controller.savefile_str)
        elif trigger == 3:
            self.display('Current ui module: %s'%self.controller.ui.ui_str)
        elif trigger == 4:
            raise ScreenDoneException
        elif trigger == 5:
            mainmenu = DefaultMenu(self.controller)
            self.after_me_goto(mainmenu)
    def __repr__(self):
        return "Special Action Menu"

class DefaultMenu(BaseScreen):
    def __init__(self, controller):
        BaseScreen.__init__(self, controller)
    def __repr__(self):
        return "Main Menu"

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

class DecorationScreen(BaseScreen):
    def __init__(self, controller):
        BaseScreen.__init__(self, controller)
    def run(self):
        raise ScreenDoneException
    def set_state(self):pass
    def __repr__(self):
        return "decoration"




