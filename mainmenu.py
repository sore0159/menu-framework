import sys
import argparse
import os

import gamepackage
import uimodules
from default.controller import ScreenController

###########
controller_lastfile = 'savedata/'+sys.argv[0][:-3]+'.rc'
controller_fixedfile = 'config.rc'

def check_config_files():
    sv_expand = gamepackage.saves.expand_savefile_name
    ui_expand = uimodules.expand_uimodule_name
    ui_str = None
    savefile_str = None
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
                        savefile_str = temp_save
                elif line[:9] == 'FIXD UI =':
                    temp_ui = line[9:].strip()
                    if ui_expand(temp_ui) in sys.modules:
                        ui_str = temp_ui
        fixedfile.close()
    try:
        lastfile = open(controller_lastfile)
    except IOError:
        pass
    else:
        for i,line in enumerate(lastfile):
            if i > 10: break  # just a saftey
            if len(line)>10:
                if not savefile_str and line[:9] == 'LAST SV =':
                    temp_save = line[9:].strip()
                    if os.path.isfile(sv_expand(temp_save)):
                        savefile_str = temp_save
                elif not ui_str and line[:9] == 'LAST UI =':
                    temp_ui = line[9:].strip()
                    if ui_expand(temp_ui) in sys.modules:
                        ui_str = temp_ui
        lastfile.close()
    return ui_str, savefile_str

def write_config_file(last_save, last_ui):
    try:
        config_file = open(controller_lastfile, 'w')
    except IOError:
        pass
    else:
        config_file.write("##### COMPUTER GENERATED #####\n")
        if last_save:
            config_file.write('LAST SV = '+last_save+'\n')
        if last_ui:
            config_file.write('LAST UI = '+last_ui+'\n')
        config_file.close()



if __name__ == '__main__':
    ##### let the gamepackage decide how save files are handled
    savefile_list = gamepackage.saves.get_savefile_list()
    savefile_help_str = gamepackage.saves.savefile_help_str
    ##### I guess let the ui package decide how the ui modules are handled?
    uimodule_list = uimodules.uimodule_list
    ui_help_str = uimodules.ui_help_str
    argparser = argparse.ArgumentParser(description='========== GORILLA ISLAND MAIN MENU ==========', epilog='Associated Files: config.rc has variables "FIXD SV =" and "FIXD UI =" you can use to set default startup arguments: command line arguements passed at runtime, if present, will override these options.  Also savedata/mainmenu.rc will try to store data on your UI and savefile when you quit, but this will be overridden by either commandline options or FIXED vars, if present.')
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
    ###### okay now check config files
    config_ui, config_save = check_config_files()
    if not uimodule_str: uimodule_str = config_ui
    if not savefile and not new: savefile = config_save
    #### OKAY READY GO
    controller = ScreenController(uimodule_str, savefile, new)
    controller.run_loop()
    #### Wrap up
    savefile, ui_mod = controller.last_usage_info()
    write_config_file(savefile, ui_mod)
   
