from collections import defaultdict
####### CONTENTS #######
# BaseScreen
# DefaultSpecials
# ScreenDoneException
# QuitException
# CloseMenusException
#
# DecorationScreen
# MicroMenu
#######################

class ScreenDoneException(Exception):
    def __init__(self, norefresh=False, next_screen=None, die=True, savefile=None, uimodule=None, *args, **kwargs):
        Exception.__init__(self, *args)
        self.norefresh = norefresh
        self.next_screen = next_screen
        self.die = die
        self.savefile = savefile
        self.uimodule = uimodule
class QuitException(Exception): pass
class CloseMenusException(Exception):
    def __init__(self, then_open = None, *args):
        Exception.__init__(self, *args)
        self.then_open = then_open
##################################################
class DebugDescr(object):
    def __get__(self, instance, owner):
        return instance._debug
    def __set__(self, instance, val):
        print "PING %s %s"%(instance, val)
        instance._debug = val

class BaseScreen(object):
    def __init__(self, default_bubble=1):
        self.name = 'Base Screen'
        ###### Config Vars
        self.default_specials = True
        self.no_display = False
        self.is_menu = True
        ###### State Information
        self.bubbles = defaultdict(list)
        self.default_bubble = default_bubble
        self.event_so_far = ''
        self.ignored_chars = ''
        self.temp_display_list = []
        self.display_flag = True
        self.event_triggers = {}
        self.controller_info = {}
    def __repr__(self):
        return self.name
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
    def del_state(self, bubble):
        self.bubbles.pop(bubble, None)
    def display(self, text, **kwargs):
        self.temp_display_list.append((text, kwargs))
    def state(self, text, **kwargs):
        if 'bubble' in kwargs:
            bubble = kwargs.pop('bubble')
        else:
            bubble = self.default_bubble
        self.bubbles[bubble].append((text, kwargs))
    #######################################
    def run(self, controller):
        self.get_controller_info(controller)
        if not self.no_display and self.display_flag:
            self.set_state()
            controller.full_display()
            self.display_flag = False
        trigger = self.get_event(controller)
        if trigger: 
            self.display_flag = True
            self.execute_trigger(trigger)

    def get_event(self, controller):
        base_event = controller.get_event()
        if self.default_specials: 
            if base_event == '#':
                self.event_so_far = ''
                self.trigger_specials()
                return 0
        ####
        prev_event = self.event_so_far
        event = self.event_so_far + base_event
        poss_matches = [x for x in self.event_triggers if x[:len(event)] == event]
        if not poss_matches and prev_event in self.event_triggers:
            controller.put_event_back(base_event)
            return self.event_match(prev_event)

        while event and not poss_matches:
            poss_matches = [x for x in self.event_triggers if x[:len(event)] == event]
            if not poss_matches: 
                ignored, event = event[:1], event[1:]
                self.ignored_chars += ignored
        self.event_so_far = event
        if base_event == '\n':
            return self.event_fail()
        else:
            return 0
    ##################################################
    def trigger_specials(self):
        specialscreen = DefaultSpecials()
        raise ScreenDoneException(die=False, next_screen=specialscreen)

    def event_fail(self):
        fail_event = self.ignored_chars.strip()
        if fail_event: self.fail_message(fail_event)
        self.ignored_chars = ''
        return False

    def event_match(self, event):
        self.display('')
        ignored = self.ignored_chars.strip()
        if ignored: self.ignore_message(ignored)
        self.ignored_chars = ''
        self.event_so_far = ''
        self.execute_message(event.strip())
        return self.event_triggers[event]

    ###################################################
    def fail_message(self, attempt_str):
        self.display("%s is not a valid option: type # for special options"%attempt_str)
    def ignore_message(self, ignored):
        self.display('Ignoring unmatchable input %s...'%ignored)
    def execute_message(self, event):
        self.display('Executing command %s...'%event)

    ######### OVERLOAD ########
    def get_controller_info(self, controller):
        '''DO NOT STORE LINKS'''
        info = self.controller_info

    def set_state(self):
        self.clear_state()
        self.state('Base Screen', center=1)
        self.add_trigger('q', 1)
        self.display_flag = True

    def execute_trigger(self, trigger):
        self.display('TRIGGER: %s'%trigger)
        self.display('EVENT QUEUE: '+''.join(self.event_queue))
        if trigger == 1: raise ScreenDoneException

class DecorationScreen(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
        self.name = "Decoration Template"
        self.is_menu = False
    def run(*args):
        raise ScreenDoneException
    def set_state(*args):pass

class MicroMenu(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
        self.name = "Micro Menu"
        self.no_display = True
        ###### STATE INFO ######
        self.event_triggers = {}

    def set_state(*args): pass
    def ignore_message(self, ignored):pass
    def execute_message(self, event): pass
    def get_event(self, controller):
        base_event = controller.get_event()
        prev_event = self.event_so_far
        self.event_so_far += base_event
        if base_event == '\n':
            if prev_event in self.event_triggers:
                return self.event_match(prev_event)
            else:
                return self.event_fail()
        else:
            return 0

    def event_match(self, event):
        return self.event_triggers[event]
    def event_fail(self):
        fail_event = self.event_so_far.strip()
        if fail_event: self.fail_message(fail_event)
        else:self.display(self.helpstr)
        raise ScreenDoneException(norefresh=True)
    ############## OVERLOAD ##############
    def fail_message(self, event_str):
        self.display("'%s' is an invalid quick option!"%event_str)
        self.display(self.helpstr)
    def execute_trigger(self, trigger):
        raise ScreenDoneException(norefresh=True)

class DefaultSpecials(MicroMenu):
    def __init__(self):
        MicroMenu.__init__(self)
        self.name = "Default Specials"
        ###### STATE INFO ######
        self.event_triggers = {'quit':1, 'file':2, 'ui':3, 'refresh':4, 'menu':5, 'help':6, 'resume':7}
        self.helpstr = "Special options: "+' '.join(['#'+x.strip() for x in sorted(self.event_triggers)])+'\nType #help to for full description'
        #####

    def get_controller_info(self, controller):
        '''DO NOT STORE LINKS'''
        info = self.controller_info
        if info: return
        bool1 = (not controller.current_screen.is_menu and not controller.menu_queue)
        info['savefile'] = controller.savefile_str
        info['uimodule'] = controller.ui.ui_str
        if bool1 or not info['savefile']:
            self.event_triggers.pop('resume')
            self.helpstr = self.helpstr.replace('#resume', '(#resume)')

    def fail_message(self, event_str):
        if event_str and event_str == 'resume':
            if not self.controller_info['savefile']:
                self.display("You do not have a game loaded!")
            else:
                self.display("You are already in game!")
        else:
            self.display("'%s' is an invalid special option!"%event_str)
            self.display(self.helpstr)
    def execute_trigger(self, trigger):
        info = self.controller_info
        if trigger == 1:
            raise QuitException
        elif trigger == 2:
            self.display('Current save file: %s'%info['savefile'])
        elif trigger == 3:
            self.display('Current ui module: %s'%info['uimodule'])
        elif trigger == 4:
            raise ScreenDoneException
        elif trigger == 5:
            raise CloseMenusException(then_open='main')
        elif trigger == 6:
            self.long_help_display()
        elif trigger == 7:
            raise CloseMenusException
        elif trigger == 8:
            self.display(self.helpstr)
        raise ScreenDoneException(norefresh=True)

    def long_help_display(self):
        long_help = '''Special commands:
#file       -- Display the current savegame file
#help       -- Display this information
#menu       -- Go to the Main Menu
#quit       -- Quit the game entirely (saving your progress)
#refresh    -- Redraw the screen (handy if failed prompt messages are in your way)
#resume     -- Close all menus and return to the game in progress
#ui         -- Display the current active UI module'''
        self.display(long_help)

