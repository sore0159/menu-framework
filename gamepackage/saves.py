import os
from screens.templates import ScreenDoneException, DefaultScreen

savefile_list = [(x[:-4], 'savedata/'+x)[i] for x in os.listdir('savedata') if x[-4:]=='.shv' for i in (0,1)]
savefile_help_str = 'Valid forms: savedata/FILENAME.shv or FILENAME'
def savefile_arg_parse(savefile_arg):
    if savefile_arg and savefile_arg[-4:] == '.shv':
        return savefile_arg[9:-4]
    else:
        return savefile_arg

def load_savefile(controller, savefile_str):
    game_screen = DefaultScreen(controller)
    screen_q = []
    return game_screen, screen_q
def save_state(controller, savefile_str):
    pass

def new_game(controller):
    game_screen = DefaultScreen(controller)
    screen_q = []
    savefile_str = 'blah'
    return savefile_str, game_screen, screen_q

def expand_savefile_name(name):
    return 'savedata/'+name+'.shv'
