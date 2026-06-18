import os 
import subprocess
import sys
import shutil


def venv_name(reader):
    return f".{reader.__name__.lower()}-venv"





def is_venv(base_path,reader):
    dedicated_venv = venv_name(reader)
    os.path.join(base_path,dedicated_venv)
    return os.path.exists(dedicated_venv)


def make_dedicated_venv(base_path,reader):
    """makes a dedicated venv for the reader, it also installs its dependencies"""
    dedicated_venv = venv_name(reader)
    subprocess.run(["python.exe","-m","venv",dedicated_venv])
    that_python = os.path.join(base_path,dedicated_venv,"Scripts","python.exe")
    subprocess.run([that_python,"-m","pip","install","-r",reader.requirements])

def remove_venv(base_path,reader):
    dedicated_venv = venv_name(reader)
    the_venv = os.path.join(base_path,dedicated_venv)
    if os.path.join(base_path,sys.prefix) == the_venv:
        print("current venv")
        return False
    else:
        try:
            shutil.rmtree(the_venv,ignore_errors=True)
            return True
        except Exception as e:
            print(e)
            return False

if __name__ == "__main__":
    from helpers.bookreaders import KokoroReader
    is_venv(base_path=".",reader=KokoroReader)


