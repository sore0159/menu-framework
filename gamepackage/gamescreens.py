from screens.defaults import BaseScreen

class GameScreen(BaseScreen):
    def __init__(self):
        self.count = 0
        BaseScreen.__init__(self)
        self.is_menu = False

    def __repr__(self):
        return "Game Menu"

    def set_state(self, controller=None):
        self.clear_state()
        self.state('Game Screen', center=2)
        self.state('The count is: %s'%self.count)
        self.state('(c)Count', indent=1)
        self.add_trigger('c', 3)

    def execute_trigger(self, controller, trigger):
        if trigger == 3: 
            self.count +=1
            self.set_state()
