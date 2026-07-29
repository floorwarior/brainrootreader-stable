import json
import os
from helpers.bookreaders import readers as builtin_readers
from plusreaders import readers as plus_readers
from helpers.get_root import getroot
from tomlkit.toml_document import TOMLDocument
from tomlkit import parse as tomlkit_parse
from tomlkit import dump as tomlkit_dumps
from warnings import warn

all_readers = {**builtin_readers,**plus_readers}
BASE_PATH = getroot()

def _valid_fallback_order(fallbackorder):
    for item in fallbackorder:
        if item not in list(all_readers.keys()):
            return False

    return True


def get_all_readers():
    return list(all_readers.keys())


_TOML_SCHEMA = {
    "app.port":{
        "type":int,
        "default":5003
    },
    "app.audio_method":{
        "type":str,
        "options":["subprocess","threading"],
        "default":"threading"
    },
    "app.debug":{
        "type":bool,
        "default":False
    },
    "app.host":{
        "type":str,
        "default":"localhost",
        "options":["localhost","0.0.0.0"]
    },
    "subprocess.core_count":{
        "type":int,
        "default":2
    },
    "subprocess.use":{
        "type":str,
        "options":["ReaderCoreConnector"],
        "default":"ReaderCoreConnector"
    },
    "subprocess.starting_port":{
        "type":int,
        "default":4222,
    },
    "subprocess.throttle":{
        "type":bool,
        "default":False
    },
    "subprocess.throttle_step":{
        "type":int
    },
    "subprocess.throttle_for":{
        "type":int,
        "default":5
    },
    "style.theme":{
        "type":str,
        "options":["NEW_THEME","OLD_THEME"],
        "default":"NEW_THEME"
    },
    "startup.loading_window":{
        "type":bool,
        "default":True
    },
    "shutdown.shutdown_after":{
        "type":int,
        "default":60*60*20
    },
    "shutdown.auto_shutdown":{
        "type":bool,
        "default":False
    },
    "reader.selected_reader":{
        "type":str,
        "options":get_all_readers()
    },
    "reader.fallback_order":{
        "type":list,
        "validate":_valid_fallback_order
    }
}




def get_field(data,dotnotation):
    """returns the current value of a dotnotatio
    usage:
    ```
    port = get_field(CONFIG,"app.port")
    print(port)
    >> 5003
    ```
    """
    current = data
    keys = dotnotation.split(".")
    for key in keys:
        current = current[key]
    return current


def valid_field(dotnotation,value):
    """checks to see if the value is valid for that field
    
    example usage:
    if valid_field("app.port",5003):
        print(5003,"is a valid port")
    
    
    """

    sch = _TOML_SCHEMA.get(dotnotation,False)
    if not sch:
        raise KeyError("Not a valid key")

    valid_type = sch.get("type")
    validate = sch.get("validate")
    #default = sch.get("default")
    options = sch.get("options")


    if not isinstance(value,valid_type):
        if valid_type == int:
            try:
                value = int(value)
            except:
                warn(message=f"{dotnotation} does not accept {value} as it is not {valid_type}")
                return False
        else:
            warn(message=f"{dotnotation} does not accept {value} as it is not {valid_type}")
            return False
            #raise ValueError(f"{dotnotation} does not accept {value} as it is not {valid_type}")
        
    if validate:
        if not validate(value):
            warn(message=f"{value} did not pass the validations check for {dotnotation}")
            return False
            #raise ValueError(f"{value} did not pass the validations check for {dotnotation}")
        

    if options and value not in options:
        warn(message=f"{value} is not a valid for {dotnotation}, options: {options}")
        return False
        #raise ValueError(f"{value} is not a valid value, options: {options}")

    return True



def validate_config_file(CONFIG):
    for dotnotation in _TOML_SCHEMA.keys():
        value = get_field(CONFIG,dotnotation)
        if not valid_field(dotnotation,value):
            return False

    return True


def edit_field(data,dotnotation,value) -> bool:
    "Modifies the loaded config file in place you will have to call save_settings after"
    current = data

    if not valid_field(dotnotation=dotnotation,value=value):
        return False
    keys = dotnotation.split(".")
    for key in keys[:-1]:
        try:
            current = current[key]
        except:
            return False
    current[keys[-1]] = value
    return True

# def save_settings(base_path,data):
#     #saves the settings into the config for all the readers
#     readers = {}
#     for key,val in data.items():
#         current_reader,subkey = key.rsplit("_")
#         if val == "empty" or  not (current_reader in all_readers.keys()):
#             if val != "empty":
#                 if key == "global_reader":
#                     set_global_reader(global_reader=val)

#             continue
#         if not current_reader in readers:
#             readers[current_reader] = {subkey:val}
#         else:
#             readers[current_reader][subkey] = val
    
#     for reader, subdict in readers.items():
#         config_reader(reader,subdict)


def get_toml_config_path(basepath):
    return os.path.join(basepath,"appconfig.toml")

# def load_app_config(basepath=None):
#     #gets the current app config file
#     if not basepath:
#         raise BaseException("you did not supply a basepath")
#     configfile = os.path.join(basepath,"appconfig.json")
#     with open(configfile,"r") as file:
#         data = json.load(file)
#         return data
    


def load_app_config_v2(basepath=None):
    if not basepath:
        raise BaseException("you did not supply a basebath")
    with open(get_toml_config_path(basepath=basepath),"r") as f:
        config = tomlkit_parse(f.read())
        if validate_config_file(config):
            return config
        else:
            raise ValueError("Config File contains invalid values.")

def save_config_file(data:TOMLDocument,basepath:str):
    """takes a modified tomldocument and save it"""
    if not isinstance(data,TOMLDocument):
        raise ValueError("data is not type TomlDocument you can only edit tomldocument items")
    
    with open(get_toml_config_path(basepath=basepath),"w") as new:
        tomlkit_dumps(data,new)




BRRAPPCONFIG = load_app_config_v2(basepath=BASE_PATH)