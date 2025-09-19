import json
import os
from helpers.bookreaders import readers as builtin_readers
from plusreaders import readers as plus_readers
from readerconfigs import config_reader,set_global_reader


all_readers = {**builtin_readers,**plus_readers}


def save_settings(base_path,data):
    """saves the settings into the config for all the readers"""
    readers = {}
    for key,val in data.items():
        current_reader,subkey = key.rsplit("_")
        if val == "empty" or current_reader not in all_readers.keys():
            if val != "empty":
                if key == "global_reader":
                    set_global_reader(global_reader=val)

            continue
        if not current_reader in readers:
            readers[current_reader] = {subkey:val}
        else:
            readers[current_reader][subkey] = val
    
    for reader, subdict in readers.items():
        config_reader(reader,subdict)
        
        
