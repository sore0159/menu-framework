from collections import defaultdict
####### CONTENTS #######
# DecorationScreen
# SpecialCommandCatcher
# TemplateScreen
# ScreenDoneException
# QuitException
#######################

class ScreenDoneException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        self.norefresh = kwargs.get('norefresh', 0)
class QuitException(Exception):pass

class TemplateScreen(object):
    def __init__(self, default_bubble=1):
        self.default_specials = True
        self.no_display = False
        self.display_flag = True
        self.is_menu = True
        self.bubbles = defaultdict(list)
        self.default_bubble = default_bubble
        self.event_queue = []
        self.clear_triggers()
        self.temp_display_list = []
    def display(self, text, **kwargs):
        self.temp_display_list.append((text, kwargs))
    def get_event(self, controller):
        base_event = controller.get_event()
        event = base_event
        if self.default_specials: 
            if event == '#':
                self.event_queue = []
                self.trigger_specials(controller)
                return 0
        for char in reversed(self.event_queue+['']):
            event = char+event
            if event in self.event_triggers:
                self.event_queue = []
                self.event_display(event)
                return self.event_triggers[event]
        else:
            if base_event != '\n': self.event_queue.append(base_event)
            elif base_event == '\n' and self.event_queue:
                attempt = ''.join(self.event_queue)
                self.event_queue = []
                self.fail_message(attempt)
            return 0
    def fail_message(self, attempt_str):
        self.display("%s is not a valid option: type # for special options"%attempt_str)
    def event_display(self, event):
        self.display('\nExecuting command %s...'%event.strip())
    def clear_triggers(self):
        self.event_triggers = {}
    def add_trigger(self, event_str, trigger_int):
        self.event_triggers[event_str] = trigger_int
    def clear_state(self, **kwargs):
        if 'bubble' in kwargs:
            bubble = kwargs.pop('bubble')
            if 'triggers' in kwargs:
                self.clear_triggers()
        else:
            self.clear_triggers()
            bubble = self.default_bubble
        self.bubbles[bubble] = []
    def state(self, text, **kwargs):
        if 'bubble' in kwargs:
            bubble = kwargs.pop('bubble')
        else:
            bubble = self.default_bubble
        self.bubbles[bubble].append((text, kwargs))
    def after_me_goto(self, controller, screen):
        if screen.is_menu:
            controller.menu_queue.append(screen)
        else:
            controller.screen_queue.append(screen)
    def run(self, controller):
        if self.display_flag:
            self.set_state(controller)
            controller.full_display()
        trigger = self.get_event(controller)
        if trigger: 
            self.display_flag = True
            self.execute_trigger(controller, trigger)
        else: 
            self.display_flag = False

    ######### OVERLOAD ########
    def __repr__(self):
        return "Template Menu"
    def trigger_specials(self, controller):
        specials = {'help':1}
        specialscreen = SpecialCommandCatcher(specials)
        controller.add_screen(specialscreen)
    def set_state(self, controller=None):
        self.clear_state()
        self.state('Template Screen', center=1)
        self.add_trigger('q', 1)
        self.display_flag = True

    def execute_trigger(self, controller, trigger):
        self.display('TRIGGER: %s'%trigger)
        self.display('EVENT QUEUE: '+''.join(self.event_queue))
        if trigger == 1: raise ScreenDoneException

class SpecialCommandCatcher(TemplateScreen):
    def __init__(self, special_dict):
        TemplateScreen.__init__(self)
        self.no_display = True
        self.specials = special_dict
        self.event_so_far = ''
        self.helpstr = "Valid special options: "+' '.join([x.strip() for x in self.specials])
    def get_event(self, controller):
        base_event = controller.get_event()
        return base_event
    def set_state(*args):pass
    def run(self, controller):
        event = self.get_event(controller)
        self.event_so_far += event
        if self.event_so_far in self.specials:
            self.execute_special(controller, self.specials[self.event_so_far])
            raise ScreenDoneException(norefresh=1)
        else:
            ev_len = len(self.event_so_far)
            if event == '\n' and self.event_so_far not in [x[:ev_len] for x in self.specials]:
                self.fail_message(self.event_so_far.strip())
                raise ScreenDoneException(norefresh=1)

    ###### OVERLOAD #######
    def execute_special(self, controller, trigger):
        pass
    def fail_message(self, event_str):
        if event_str and event_str !='help':
            self.display("'%s' is an invalid special option!"%self.event_so_far.strip())
        self.display(self.helpstr)
    def __repr__(self):
        return "Special Command Catcher"

class DecorationScreen(TemplateScreen):
    def __init__(self):
        TemplateScreen.__init__(self)
        self.is_menu = False
    def run(*args):
        raise ScreenDoneException
    def set_state(*args):pass
    def __repr__(self):
        return "decoration"



