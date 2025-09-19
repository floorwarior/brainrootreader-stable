"""
def get_plugin_readers():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"plusreadersbyname.json")) as plusreaders:
        readers :dict = json.load(plusreaders)
    

    for module, classname in readers.items():
        module_ = importlib.import_module(module, package="plusreaders")
        class_obj = module_.__getattribute__(classname)
        globals()[classname] = class_obj

"""

import importlib
import os
import json


readers = {}


def get_plugin_readers():
    # Get the current package name
    package_name = __name__.rpartition('.')[0] or __name__
    if package_name == '__main__':
        package_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plusreadersbyname.json")) as plusreaders:
        readers_data: dict = json.load(plusreaders)
    
    for module_name, classname in readers_data.items():
        try:
            # Import using absolute path
            module_ = importlib.import_module(f".{module_name}", package=package_name)
            class_obj = getattr(module_, classname)
            globals()[classname] = class_obj
            readers[classname] = class_obj
            print(f"Successfully imported {classname} from {module_name}")
        except ImportError as e:
            print(f"Failed to import {classname} from {module_name}: {e}")
        except AttributeError as e:
            print(f"Class {classname} not found in {module_name}: {e}")


get_plugin_readers()