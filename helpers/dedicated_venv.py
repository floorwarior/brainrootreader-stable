import os 
import subprocess
import sys
import shutil


def venv_name(reader):
    return f".{reader.__name__.lower()}-venv"



def is_venv(base_path,reader:object):
    dedicated_venv = venv_name(reader)
    os.path.join(base_path,dedicated_venv)
    return os.path.exists(dedicated_venv)



def make_dedicated_venv(base_path,reader):
    """makes a dedicated venv for the reader, it also installs its dependencies"""
    dedicated_venv = venv_name(reader)
    if reader.recommended_python == "any":
        venv_ok = subprocess.run(["python.exe","-m","venv",dedicated_venv]) 
    else:
        venv_ok = subprocess.run(["py",f"-{reader.recommended_python}","-m","venv",dedicated_venv]) 
    if not venv_ok.returncode == 0:
        print(f"venv could not be created for {reader.__name__}, error: {venv_ok.stdout}")
        return False
    that_python = os.path.join(base_path,dedicated_venv,"Scripts","python.exe")
    result = subprocess.run([that_python,"-m","pip","install","-r",reader.requirements])
    return result.returncode == 0

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


