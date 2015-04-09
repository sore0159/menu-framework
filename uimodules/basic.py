from collections import deque
from screens.templates import QuitException, ScreenDoneException
  ######  Required by Menus:  ######
# display(text, flag)
# query(choices, special_choices)

class UI(object):
    def __init__(self):
        self.left_padding = 4
        self.display_width = 70
        self.event_queue = deque()

    def wrap_text(self, text, width):
        if not text: return ['']
        wrap_list = []
        line_list = text.splitlines()
        for line in line_list:
            wordlist = line.split(' ')
            tic = 0
            for word in wordlist:
                if tic and len(wrap_list[-1]) + len(word) < width:
                    wrap_list[-1]+=' '+word
                elif len(word) < width:
                    wrap_list.append(word)
                else:
                    while word:
                        temp_chars, word = word[:width], word[width:]
                        wrap_list.append(temp_chars)
                tic = 1
        return wrap_list

    def display(self, text, **kwargs):
        if 'center' in kwargs:
            deco = kwargs['center']
            deco_char = {1:'=', 2:'-', 3:' ', 4:'+'}.get(deco, ' ')
            max_text_width = {}.get(deco, 30)
        else: max_text_width = self.display_width
        l_pad = ' '*self.left_padding
        wrap_list = self.wrap_text(text, max_text_width)
        for line in wrap_list:
            if 'center' in kwargs:
                line =  (' '+line+' ').center(self.display_width, deco_char)
            print l_pad+line


    def get_event(self):
        try:
            return self.event_queue.pop()
        except IndexError:
            try:
                user_event = raw_input('\n>>> ')
            except (EOFError, KeyboardInterrupt):
                self.display('')
                raise QuitException
            if not user_event: 
                return ''
            else:
                self.event_queue.extendleft(user_event)
                return self.event_queue.pop()


