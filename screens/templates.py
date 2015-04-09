class ScreenDoneException(Exception): pass
class QuitException(Exception):pass

class DefaultScreen(object):
    def __init__(self, controller):
        self.controller = controller
        self.previous_screen = controller.current_screen
        temp_depth = (len(self.controller.screen_queue)+1)
        if self.controller.current_screen: temp_depth+=1
        self.state = 'DEPTH:%s'%temp_depth+'\n%s'%self.controller.file_data

        self.num_events = 0
        self.while_gone = 0
    def missed_event(self):
        self.while_gone +=1
        if self.previous_screen:
            self.previous_screen.missed_event()
    def get_event(self):
        self.num_events +=1
        if self.previous_screen:
            self.previous_screen.missed_event()
        return self.controller.get_event()
    def display(self, text, **kwargs):
        self.controller.display(text, **kwargs)
    def new_screen(self, screen):
        self.controller.new_screen(screen)
    def run(self):
        self.display(self.state, center=2)
        if self.while_gone:
            self.display('%s EVENTS WHILE GONE'%self.while_gone)
            self.while_gone = 0
        event = self.get_event()
        self.display('EVENT #%s: %s'%(self.num_events, event))
        if event == 'n':
            self.new_screen(DefaultScreen(self.controller))
            return
        elif event == 'q':
            raise ScreenDoneException
