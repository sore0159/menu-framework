from collections import deque
from screens.templates import QuitException, ScreenDoneException
from . import basic
  ######  Required by Menus:  ######
# display(text, flag)
# query(choices, special_choices)

class UI(basic.UI):
    def __init__(self):
        self.ui_str = 'screamer'
        self.left_padding = 15
        self.display_width = 50
        self.event_queue = deque()
        self.input_prompt = '\n!!! '
        self.char_dict = {1:'=', 2:'-', 3:' ', 4:'+'}
    def display(self, text, **kwargs):
        basic.UI.display(self, text.upper(), **kwargs)



