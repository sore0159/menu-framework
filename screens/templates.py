####### CONTENTS #######
# DecorationScreen
# SpecialCommandCatcher
# TemplateScreen
# ScreenDoneException
# QuitException
#######################

class ScreenDoneException(Exception): pass
class QuitException(Exception):pass

class TemplateScreen(object):
    def __init__(self, controller, default_bubble=1):
        self.default_specials = True
        self.no_display = False
        self.display_flag = True
        self.is_menu = True
        self.controller = controller
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
                self.trigger_specials()
                return 0
            elif event == '\n' and self.event_queue:
                attempt = ''.join(self.event_queue)
                self.event_queue = []
                self.display("%s is not a valid option: type # for special options"%attempt)
        for char in reversed(self.event_queue+['']):
            event = char+event
            if event in self.event_triggers:
                self.event_queue = []
                self.event_display(event)
                return self.event_triggers[event]
        else:
            if base_event != '\n': self.event_queue.append(base_event)
            return 0
    def event_display(self, event):
        self.display('\nExecuting command %s...'%event.strip())
    def clear_triggers(self):
        self.event_triggers = {}
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
        if screen.is_menu:
            self.controller.menu_queue.append(screen)
        else:
            self.controller.screen_queue.append(screen)
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
    def trigger_specials(self):
        specials = {'help':1}
        specialscreen = SpecialCommandCatcher(self.controller, specials)
        self.controller.add_screen(specialscreen)
    def set_state(self):
        self.clear_state()
        self.state('Template Screen', center=1)
        self.add_trigger('q', 1)
        self.display_flag = True

    def execute_trigger(self, trigger):
        self.display('TRIGGER: %s'%trigger)
        self.display('EVENT QUEUE: '+''.join(self.event_queue))
        if trigger == 1: raise ScreenDoneException

class SpecialCommandCatcher(TemplateScreen):
    def __init__(self, controller, special_dict):
        TemplateScreen.__init__(self, controller)
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
                self.fail_message(self.event_so_far.strip())
                self.die()

    ###### OVERLOAD #######
    def execute_special(self, trigger):
        pass
    def fail_message(self, event_str):
        if event_str and event_str !='help':
            self.display("'%s' is an invalid special option!"%self.event_so_far.strip())
        self.display(self.helpstr)
    def __repr__(self):
        return "Special Command Catcher"

class DecorationScreen(TemplateScreen):
    def __init__(self, controller):
        TemplateScreen.__init__(self, controller)
        self.is_menu = False
    def run(self):
        raise ScreenDoneException
    def set_state(self):pass
    def __repr__(self):
        return "decoration"



