import sys
import argparse
import os

import gamepackage
import uimodules
from screens.controller import ScreenController

###########
controller_lastfile = 'savedata/'+sys.argv[0][:-3]+'.rc'
controller_fixedfile = 'config.rc'

def check_config_files(last_flag = False):
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
            if i > 30: break  # just a saftey
            if len(line)>10:
                if line[:10] == 'FIXED SV =':
                    temp_save = line[10:].strip()
                    if os.path.isfile(sv_expand(temp_save)) or temp_save.upper()=='LAST':
                        savefile_str = temp_save
                elif line[:10] == 'FIXED UI =':
                    temp_ui = line[10:].strip()
                    if ui_expand(temp_ui) in sys.modules or temp_ui.upper=='LAST':
                        ui_str = temp_ui
        fixedfile.close()
    if any([last_flag, (savefile_str and savefile_str.upper() == 'LAST'), (ui_str and ui_str.upper() == 'LAST')]):
        try:
            lastfile = open(controller_lastfile)
        except IOError:
            pass
        else:
            for i,line in enumerate(lastfile):
                if i > 10: break  # just a saftey
                if len(line)>10:
                    if (not savefile_str or savefile_str.upper() == 'LAST') and line[:9] == 'LAST SV =':
                        temp_save = line[9:].strip()
                        if os.path.isfile(sv_expand(temp_save)):
                            savefile_str = temp_save
                    elif (not ui_str or ui_str.upper() == 'LAST') and line[:9] == 'LAST UI =':
                        temp_ui = line[9:].strip()
                        if ui_expand(temp_ui) in sys.modules:
                            ui_str = temp_ui
            lastfile.close()
    if ui_str and ui_str.upper() == 'LAST': ui_str = None
    if savefile_str and savefile_str.upper() == 'LAST': savefile_str = None
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
    ######
    argparser = argparse.ArgumentParser(description='Python Menu Framework for Abstract Game', epilog='Associated Files: config.rc has variables "FIXED SV =" and "FIXED UI =" you can use to set defaults: read there for more.')
    ###### I'D LIKE TO HAVE AN ARGUMENT ######
    # I bet that's in a lot of comments of people who use argparser
    argparser.add_argument('-u', '--uimodule', default=None, help=ui_help_str , metavar='UIMODULE', choices=uimodule_list)
    savegroup = argparser.add_mutually_exclusive_group()
    savegroup.add_argument('savefile', nargs='?', metavar='SAVEFILE', help=savefile_help_str, default=None, choices=savefile_list)
    savegroup.add_argument('-n', '--new', help='Create a new game: conflicts with SAVEFILE arg and -l', action='store_true')
    savegroup.add_argument('-l', '--last', help='Load last played game (if able): conflicts with SAVEFILE arg and -n', action='store_true')
    parsed_args = argparser.parse_args()  # YOU HAD ONE JOB
    if parsed_args.new:
        savefile = None
        new = True
    elif parsed_args.last:
        savefile = None
        new = False
    else:
        savefile = gamepackage.saves.savefile_arg_parse(parsed_args.savefile)
        new = False
    uimodule_str = uimodules.parse_ui_arg(parsed_args.uimodule)
    ###### okay now check config files
    config_ui, config_save = check_config_files(last_flag=parsed_args.last)
    if not uimodule_str: uimodule_str = config_ui
    if not savefile and not new: savefile = config_save
    #### OKAY READY GO
    controller = ScreenController(uimodule_str, savefile, new)
    controller.run_loop()
    #### Wrap up
    savefile, ui_mod = controller.last_usage_info()
    write_config_file(savefile, ui_mod)
   
