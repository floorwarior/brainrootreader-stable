import json
import os




filelocation = os.path.dirname(__file__)
GLOBALREADERCONFIG = None
reader_configs_pairs = {}




def _load_global_config():
    global GLOBALREADERCONFIG
    with open(os.path.join(filelocation,"globalreader.json")) as global_rd:
        GLOBALREADERCONFIG = json.load(global_rd)
    return GLOBALREADERCONFIG
_load_global_config()

def _load_reader_configs():
    global reader_configs_pairs
    with open(os.path.join(filelocation,"readerconfigs.json")) as f:
        reader_configs_pairs =  json.load(f)
_load_reader_configs()



def get_config_of_reader(readersname)->dict:
    """gets the config file location based on the readers name """
    with open(os.path.join(filelocation,reader_configs_pairs.get(readersname)),"r") as file:
        data = json.load(file)
    return data


def config_reader(readersname,data):
    """adds the new keys to the old config if there is a collision it overwrites the original key with the new value"""
    old_data = get_config_of_reader(readersname=readersname)
    with open(os.path.join(filelocation,reader_configs_pairs.get(readersname)),"w") as file:
        json.dump({**old_data,**data},file,indent=4)


   
def freshup():
    _load_global_config()
    _load_reader_configs()




def set_global_reader(*args,**kwargs):
    global_reader = kwargs.get("global_reader",None)
    if not global_reader:
        return False
    data = _load_global_config()    
    data["name"] = global_reader
    with open(os.path.join(filelocation,"globalreader.json"),"w") as f:
        json.dump(data,f,indent=4)    
    freshup()
