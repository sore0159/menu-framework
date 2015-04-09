import sys
import argparse
import os
from collections import deque

import gamepackage
import uimodules
from screens.templates import ScreenDoneException, DefaultScreen, QuitException

controller_lastfile = 'savedata/'+sys.argv[0][:-3]+'_last.rc'
controller_fixedfile = 'fixed_data.rc'

class ScreenController(object):
    def __init__(self, ui_str=None, savefile_str=None, new=False):
        ui_str, savefile_str = self.get_file_data(ui_str, savefile_str)
        if not ui_str: ui_str = 'basic'
        self.load_ui(ui_str)
        self.screen_queue = deque()
        self.current_screen = None
        if new or savefile_str:
            next_screen = self.load_game(savefile_str, new)
        else:
            next_screen = DefaultScreen(self)
        self.new_screen(next_screen)

    def load_game(self, savefile_str=None, new=False):
        if new:
            game_screen, savefile_str = gamepackage.saves.new_game(self)
        else:
            game_screen = gamepackage.saves.load_savefile(self, savefile_str)
        self.file_data['last_save'] = savefile_str
        return game_screen

    def get_file_data(self, ui_arg, savefile_arg):
        self.file_data = {}
        self.file_data['fix_ui'] = ''
        self.file_data['last_ui'] = ''
        self.file_data['fix_save'] = ''
        self.file_data['last_save'] = ''
        sv_expand = gamepackage.saves.expand_savefile_name
        ui_expand = uimodules.expand_uimodule_name
        try:
            fixedfile = open(controller_fixedfile)
        except IOError:
            pass
        else:
            for i,line in enumerate(fixedfile):
                if i > 10: break  # just a saftey
                if len(line)>10:
                    if line[:9] == 'FIXD SV =':
                        temp_save = line[9:].strip()
                        if os.path.isfile(sv_expand(temp_save)):
                            self.file_data['fix_save'] = temp_save
                            if not savefile_arg: savefile_arg = temp_save
                    elif line[:9] == 'FIXD UI =':
                        temp_ui = line[9:].strip()
                        if ui_expand(temp_ui) in sys.modules:
                            self.file_data['fix_ui'] = temp_ui
                            if not ui_arg: ui_arg = temp_ui
            fixedfile.close()
        try:
            lastfile = open(controller_lastfile)
        except IOError:
            pass
        else:
            for i,line in enumerate(lastfile):
                if i > 10: break  # just a saftey
                if len(line)>10:
                    if not savefile_arg and line[:9] == 'LAST SV =':
                        temp_save = line[9:].strip()
                        if os.path.isfile(sv_expand(temp_save)):
                            self.file_data['last_save'] = temp_save
                            savefile_arg = temp_save
                    elif not ui_arg and line[:9] == 'LAST UI =':
                        temp_ui = line[9:].strip()
                        if ui_expand(temp_ui) in sys.modules:
                            self.file_data['last_ui'] = temp_ui
                            ui_arg = temp_ui
            lastfile.close()
        return ui_arg, savefile_arg

    def write_file_data(self):
        try:
            config_file = open(controller_lastfile, 'w')
        except IOError:
            pass
        else:
            if self.file_data['last_save']:
                config_file.write('LAST SV = '+self.file_data['last_save']+'\n')
            if self.file_data['last_ui']:
                config_file.write('LAST UI = '+self.file_data['last_ui']+'\n')
            config_file.close()


    def new_screen(self, screen):
        if self.current_screen: self.screen_queue.append(self.current_screen)
        self.current_screen = screen
    def next_screen(self):
        try:
            self.current_screen = self.screen_queue.pop()
        except IndexError:
            raise QuitException
    def list_uimodules(self):
        return [x[10:] for x in sys.modules if x[:9] == 'uimodules'] 
    def load_ui(self, ui_str):
        self.file_data['last_ui'] = ui_str
        self.ui = getattr(sys.modules['uimodules.'+ui_str], 'UI')()
    def get_event(self):
        return self.ui.get_event()
    def display(self, text, **kwargs):
        self.ui.display(text, **kwargs)
    def run(self):
        self.display("Hello", center=1)
        try:
            while True:
                try:
                    self.current_screen.run()
                except ScreenDoneException:
                    self.next_screen()
        except QuitException: pass
        finally:
            self.quit()
    def quit(self):
        self.write_file_data()
        self.display("Goodbye", center=1)
        self.display("")


if __name__ == '__main__':
    ##### let the gamepackage decide how save files are handled
    savefile_list = gamepackage.saves.savefile_list
    savefile_help_str = gamepackage.saves.savefile_help_str
    ##### I guess let the ui package decide how the ui modules are handled?
    uimodule_list = uimodules.uimodule_list
    ui_help_str = uimodules.ui_help_str
    argparser = argparse.ArgumentParser(description='========== GORILLA ISLAND MAIN MENU ==========', epilog='Associated Files: fixed_data.rc has "FIXD SV =" and "FIXD UI =" vars to set default startup arguments: command line arguements passed at runtime, if present, will override these options.  Also savedata/mainmenu_last.rc will try to store data on your UI and savefile when you quit, but this will be overridden by either commandline options or FIXED vars, if present.')
    argparser.add_argument('-u', '--uimodule', default=None, help=ui_help_str , metavar='UIMODULE', choices=uimodule_list)
    arggroup = argparser.add_mutually_exclusive_group()
    arggroup.add_argument('savefile', nargs='?', metavar='SAVEFILE', help=savefile_help_str, default=None, choices=savefile_list)
    arggroup.add_argument('-n', '--new', help='Create a new game: conflicts with SAVEFILE arg', action='store_true')
    parsed_args = argparser.parse_args()  # YOU HAD ONE JOB
    if parsed_args.new:
        savefile = None
        new = True
    else:
        savefile = gamepackage.saves.savefile_arg_parse(parsed_args.savefile)
        new = False
    uimodule_str = uimodules.parse_ui_arg(parsed_args.uimodule)
    controller = ScreenController(uimodule_str, savefile, new)
    controller.run()
    
