import basic, screamer

mod_list = ['basic', 'screamer']
uimodule_list = [(x, 'uimodules/'+x+'.py')[i] for x in mod_list for i in (0,1)]
ui_help_str = 'Valid forms: uimodules/FILENAME.py or FILENAME'

def parse_ui_arg(ui_arg):
    if ui_arg and ui_arg[-3:] == '.py':
        ui_str = ui_arg[10:-3]
    else:
        ui_str = ui_arg
    return ui_str

def expand_uimodule_name(ui_name):
    return 'uimodules.'+ui_name

