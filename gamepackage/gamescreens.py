from screens.defaults import BaseScreen

class GameScreen(BaseScreen):
    def __init__(self, controller):
        self.count = 0
        BaseScreen.__init__(self, controller)

    def __repr__(self):
        return "Game Menu"

    def set_state(self):
        self.clear_state()
        self.state('Game Screen', center=2)
        self.state('The count is: %s'%self.count)
        self.state('(c)Count', indent=1)
        self.add_trigger('c', 3)

    def execute_trigger(self, trigger):
        if trigger == 3: 
            self.count +=1
            self.set_state()
