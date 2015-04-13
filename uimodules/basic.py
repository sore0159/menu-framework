from collections import deque
from screens.templates import QuitException, ScreenDoneException
  ######  Required by Menus:  ######
# display(text, flag)
# query(choices, special_choices)

class UI(object):
    def __init__(self):
        self.ui_str = 'basic'
        self.left_padding = 4
        self.display_width = 70
        self.event_queue = deque()
        self.input_prompt = '\n>>> '
        self.char_dict = {1:'=', 2:'-', 3:' ', 4:'+'}

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

    def display(self, text='', **kwargs):
        l_pad = ' '*self.left_padding
        divider = kwargs.get('divider', None)
        if divider:
            div_char = self.char_dict.get(divider, '-')
            print l_pad+(div_char*self.display_width)
            return 
        deco = kwargs.get('center', None)
        if deco:
            deco_char = self.char_dict.get(deco, ' ')
            max_text_width = {}.get(deco, 30)
        else: max_text_width = self.display_width
        if 'indent' in kwargs:
            max_text_width -= 4
            l_pad+=' '*(4*kwargs['indent'])
        wrap_list = self.wrap_text(text, max_text_width)
        for line in wrap_list:
            if 'center' in kwargs:
                line =  (' '+line+' ').center(self.display_width, deco_char)
            print l_pad+line

    def put_event_back(self, event):
        self.event_queue.append(event)

    def get_event(self):
        try:
            return self.event_queue.pop()
        except IndexError:
            try:
                user_event = raw_input(self.input_prompt)
            except (EOFError, KeyboardInterrupt):
                self.display('')
                raise QuitException
            if not user_event: 
                return '\n'
            else:
                self.event_queue.extendleft(user_event)
                self.event_queue.extendleft('\n')
                return self.event_queue.pop()


