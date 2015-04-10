from screens.templates import DefaultScreen, ScreenDoneException
from uimodules import mod_list

class UIChooser(DefaultScreen):
    def __init__(self, controller):
        DefaultScreen.__init__(self, controller)

    def set_state(self):
        self.state_list = []
    def get_event(self):
        return self.controller.get_event()
    def display(self, text, **kwargs):
        self.controller.display(text, **kwargs)
    def new_screen(self, screen):
        self.controller.new_screen(screen)
    def run(self):
        for line, arg_dict in self.state_list:
            self.display(line, **arg_dict)
        event = self.get_event()
        self.display('EVENT: %s'%event)

