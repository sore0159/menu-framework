from screens.templates import BaseScreen

class GameScreen(BaseScreen):
    def __init__(self):
        BaseScreen.__init__(self)
        self.name = "Game Menu"
        self.count = 0
        self.is_menu = False

    def set_state(self):
        self.clear_state()
        self.state('Game Screen', center=2)
        self.state('The count is: %s'%self.count)
        self.state('(c)Count', indent=1)
        self.state("What do you want to do?", bubble=12)
        self.add_trigger('c', 3)
    def run(self, controller):
        try:
            BaseScreen.run(self, controller)
        finally:
            self.del_state(12)
    def execute_trigger(self, trigger):
        if trigger == 3: 
            self.count +=1
            self.set_state()
