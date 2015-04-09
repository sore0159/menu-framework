import basic

mod_list = ['basic']
uimodule_list = [(x[10:], 'uimodules/'+x[10:]+'.py')[i] for x in mod_list for i in (0,1)]
ui_help_str = 'Valid forms: uimodules/FILENAME.py or FILENAME'

def parse_ui_arg(ui_arg):
    if ui_arg and ui_arg[-3:] == '.py':
        ui_str = ui_arg[10:-3]
    else:
        ui_str = ui_arg

def expand_uimodule_name(ui_name):
    return 'uimodules.'+ui_name

