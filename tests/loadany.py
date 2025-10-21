import sys
import os
from importlib import import_module

def import_from_path(file_path):
    """
    Import by adding the directory to sys.path temporarily.
    """
    directory = os.path.dirname(file_path)
    module_file = os.path.basename(file_path)
    module_name_from_file = os.path.splitext(module_file)[0]
    
    # Add directory to Python path
    sys.path.insert(0, directory)
    
    try:
        module = import_module(module_name_from_file)
        return module
    finally:
        # Remove the temporary path
        sys.path.pop(0)

