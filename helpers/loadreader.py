import json
import os

def load_reader(base_path,custom_readers={},builtin_readers={}):
    with open(os.path.join(base_path,"readerconfigs","globalreader.json"),"r") as reader_data:
        config_data = json.load(reader_data)
    reader_class_name = config_data["name"]
    #type_ = config_data["type"] the system should not care if its built in or not
    _all_readers = {**builtin_readers,**custom_readers}
    return _all_readers.get(reader_class_name)


def get_readers_config(base_path=None,readername="PiperReader",supress_error=False) -> dict:
    """get the config of the reader selected and returns it as a dict, base path should always point to the folder of the main file
    """
    if not base_path:
        raise BaseException("you did not supply a base path for get_readers_config function")



    with open(os.path.join(base_path,"readerconfigs","readerconfigs.json"),"r") as config_mapping:
        configmapping: dict = json.load(config_mapping)
        if readername not in configmapping.keys():
            raise BaseException(f"there is no config file for reader: {readername}, or if there is there is no config file mapped\ncheck if you actually added it into the readerconfig.json in readerconfigs")

        config_file_name = configmapping.get(readername)

    with open(os.path.join(base_path,"readerconfigs", config_file_name),"r") as f:
        res =json.load(f)
        #res["base_path"] = base_path
        print(res)
        return res




def all_readers(custom_readers,builtin_readers):
    return {**custom_readers,**builtin_readers}



