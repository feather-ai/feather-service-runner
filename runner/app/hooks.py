#------------------------------------------------------------------------------
# Feather SDK
# Proprietary and confidential
# Unauthorized copying of this file, via any medium is strictly prohibited
# 
# (c) Feather - All rights reserved
#------------------------------------------------------------------------------
import os

gFileHooks = None

def feather_hook_files(files):
    global gFileHooks
    gFileHooks = files
    for k in gFileHooks:
        print("Hook: ", k)
        gFileHooks[k].loaded = False

def feather_clear_hooks():
    global gFileHooks
    gFileHooks = None

def feather_handle_input_file(filename):
    ""

def feather_file_open_hook(*args, **kwargs):
    print("Hooking file", args)
    global gFileHooks
    if gFileHooks != None:
        filename = args[0]
        mode = args[1]
        if mode == "r" or mode == "rb" or model == "br":
            feather_handle_input_file(filename)

    r = _real_open(*args,**kwargs)
    return r

def feather_os_file_open_hook(*args, **kwargs):
    global gFileHooks
    if gFileHooks != None:
        filename = args[0]
        mode = args[1]
        if mode & os.O_RDONLY:
            feather_handle_input_file(filename)

    r = _real_os_open(*args, **kwargs)
    return r

_real_open = open
_real_os_open = os.open
open = feather_file_open_hook
os.open = feather_os_file_open_hook