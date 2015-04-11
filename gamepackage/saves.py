import os
import cPickle as pickle

def get_savefile_list():
    savefile_list = [(x[:-4], 'savedata/'+x)[i] for x in os.listdir('savedata') if x[-4:]=='.pkl' for i in (0,1)]
    return savefile_list
savefile_help_str = 'Valid forms: savedata/FILENAME.pkl or FILENAME'
def savefile_arg_parse(savefile_arg):
    if savefile_arg and savefile_arg[-4:] == '.pkl':
        return savefile_arg[9:-4]
    else:
        return savefile_arg

def get_savedgame(savefile_str):
    target = open(expand_savefile_name(savefile_str), 'rb')
    save_tuple = pickle.load(target)
    target.close()
    game_screen, screen_q = save_tuple
    return game_screen, screen_q

def save_game(controller):
    savefile_str = controller.savefile_str
    assert savefile_str
    save_tuple = (controller.current_screen, controller.screen_queue)
    target = open(expand_savefile_name(savefile_str), 'wb')
    pickle.dump(save_tuple, target, -1)
    target.close()

def get_new_savename():
    i = 0
    base_str = 'savedata/save%03d.pkl'
    savefile_str = base_str%i
    while os.path.isfile(savefile_str):
        i+=1
        savefile_str = base_str%i
    return 'save%03d'%i

def expand_savefile_name(name):
    return 'savedata/'+name+'.pkl'
