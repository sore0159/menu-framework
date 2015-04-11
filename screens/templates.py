from collections import defaultdict
import gamepackage
class ScreenDoneException(Exception): pass
class QuitException(Exception):pass

class BaseScreen(object):
    def __init__(self, controller, default_bubble=1):
        self.default_specials = 1
        self.controller = controller
        self.previous_screen = controller.current_screen
        if self.previous_screen:
            self.bubbles = self.previous_screen.bubbles
        else:
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
        self.display('Executing command %s...'%event)
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
        self.bubbles['display'] = True
    def full_display(self):
        for level, state_list in sorted(self.bubbles.items()):
            if level == 'display': continue
            for line, arg_dict in state_list:
                self.display(line, **arg_dict)
        self.bubbles['display'] = False
    def die(self):
        self.controller.next_screen()
    def after_me_goto(self, screen):
        screen.previous_screen = self.previous_screen
        self.controller.screen_queue.append(screen)
    def trigger_default_specials(self):
        specials = DefaultSpecials(self.controller)
        self.controller.add_screen(specials)
    def run(self):
        if self.bubbles['display']:
            self.full_display()
        trigger = self.get_event()
        if trigger: 
            self.bubbles['display'] = True
            self.execute_trigger(trigger)
        else: 
            self.bubbles['display'] = False

    ######### OVERLOAD ########
    def __repr__(self):
        return "Template Menu"
    def passed_event(self, event):
        return self.pass_event(event)
    def set_state(self):
        self.clear_state()
        self.state('Base Screen', center=1)
        self.add_trigger('q', 1)

    def execute_trigger(self, trigger):
        self.display('TRIGGER: %s'%trigger)
        self.display('EVENT QUEUE: '+''.join(self.event_queue))
        if trigger == 1: raise ScreenDoneException

class SpecialCommandCatcher(BaseScreen):
    def __init__(self, controller, special_dict):
        BaseScreen.__init__(self, controller)
        self.specials = special_dict
        self.event_so_far = ''
        self.helpstr = "Valid special options: "+' '.join([x.strip() for x in self.specials])
    def get_event(self):
        base_event = self.controller.get_event()
        return base_event
    def set_state(self):pass
    def die(self):
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
            self.bubbles['display']= True
        elif trigger == 5:
            mainmenu = DefaultMenu(self.controller)
            self.after_me_goto(mainmenu)
    def __repr__(self):
        return "Special Action Menu"

class DefaultMenu(BaseScreen):
    def __init__(self, controller):
        BaseScreen.__init__(self, controller)
        self.clear_state(bubble=0)
        self.state('Gorilla Island', center=1, bubble=0)
        self.clear_state(bubble=10)
        self.state('', bubble=10)
        self.state('', divider=1, bubble=10)
    def __repr__(self):
        return "Main Menu"

    def set_state(self):
        self.clear_state()
        self.clear_triggers()
        self.state('Main Menu', center=2)
        if self.previous_screen:
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

