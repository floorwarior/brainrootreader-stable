from helpers.loadreader import get_readers_config
from helpers.increment_port import get_next_port
from helpers.dedicated_venv import is_venv,venv_name,make_dedicated_venv,remove_venv
from helpers.readercore_connector_v2 import ReaderCoreConnector
from helpers.settings import all_readers
from helpers.kv import KEYS

from packaging.requirements import Requirement
from importlib.metadata import version,PackageNotFoundError
import sys
import os
import subprocess
from enum import StrEnum

j_port = get_next_port(6222,1)

class INSTALLED_IN(StrEnum):
    GLOBAL = "in_global"
    CURRENT_VENV = "current_venv"
    DEDICATED_VENV = "dedicated_venv"

class INSTALL_IN(StrEnum):
    CURRENT_VENV = "current_venv"
    DEDICATED_VENV = "dedicated_venv"


def is_installed_cached(reader,kv=KEYS):
    maybe_val = kv[f"is_installed-{reader.__name__}"]
    res = None
    if maybe_val is not None:
        res = maybe_val.value.lower() ==  "true"
    return res




def get_reqs(basepath,reader):
    """returns the requirements for a reader
        return a list of packaging.requirements.Requirement
    """
    if not hasattr(reader,"requirements"):
        return []

    with open(os.path.join(basepath,reader.requirements)) as f:
        lines = f.readlines()

    reqs :list[Requirement]= []
    for line in lines:
        if line.startswith("#"):
            continue
        if line.startswith("--"):
            continue
        if line.strip() == "":
            continue
        reqs.append(Requirement(line.strip()))

    return reqs 


def installed_reqs(basepath,reader):
    """shows what is installed for the reader"""
    reqs = get_reqs(basepath,reader)
    installed = {}
    for r in reqs:
        try:
            v = version(r.name)
            r.specifier
            installed[r.name] = v in r.specifier
        except PackageNotFoundError:
            installed[r.name] = False

    return installed




def is_installed(basepath,reader,kv=KEYS,try_cache=False):
    """checks if the reader is installed in the current venv or in a dedicated venv
        returns true if the reader is installed in the current sys.prefix or it is installed in the dedicated venv
    """
    if try_cache:
        cached : bool = is_installed_cached(reader)
        if cached != None:
            return cached


    def helper_1():
        rd_cfg = get_readers_config(basepath,reader.__name__)
        rd = reader(**rd_cfg)
        res = rd.is_ready()
        rd.clean_up()
        return res
        
    installed_in_current_venv = helper_1()


    def helper_2(reader):
        rd = ReaderCoreConnector(
            base_path = basepath,
            is_frozen = False, # DEPRICATED 
            core_count=1,
            forced_reader=reader.__name__,
            starting_port =next(j_port)
            )

        ready = rd.is_ready()
        rd.clean_up()
        return ready and is_venv(base_path=basepath,reader=reader)
    
    installed_in_dedicated_venv = helper_2(reader) and is_venv(basepath,reader)

    res = installed_in_current_venv or installed_in_dedicated_venv
    kv[f"is_installed-{reader.__name__}"] = res
    return res

def installed_where(basepath,reader:object):
    """returns enum: VENV, DEDICATED_VENV,GLOBAL and the second value is the folder of the python.exe
    installed_where always need is_installed run before it
    """

    if not is_venv(basepath,reader):
        if sys.prefix == sys.base_prefix:
            return INSTALLED_IN.GLOBAL , sys.prefix
        else:
            return INSTALLED_IN.CURRENT_VENV, sys.prefix
    else:
        return INSTALLED_IN.DEDICATED_VENV, os.path.join(basepath,venv_name(reader))

def installed_readers(base_path:str,readers:dict,try_cache :bool =False):
    """returns 2 values:
    installed and not_installed
    both of which are lists    
    """
    installed = []
    not_installed = []

    for reader in readers.values():
        res = is_installed(basepath=base_path,reader=reader,try_cache=try_cache)
        if res:
            t,where = installed_where(base_path,reader)
            installed.append(
                {"name":reader.__name__,
                 "install_type":t,
                 "installed_in":where,
                 "reader":reader}
            )
        else: not_installed.append({
            "name":reader.__name__
        })


    return installed, not_installed


def _get_removeable_packages(basepath,all_readers,reader_to_uninstall):
    """
    collects the requirements of currently installed readers
    checks what packages should be blocked from being removed
    - if reader a is being removed and reader b uses the same package we filter it out
    """
    currently_installed,not_installed = installed_readers(basepath,all_readers,try_cache=True)
    to_uninstall = get_reqs(basepath,reader_to_uninstall)

    currently_installed = [reader for reader in currently_installed if reader["name"] != reader_to_uninstall.__name__]
    other = []
    for remain in currently_installed:
        other += get_reqs(basepath,remain["reader"])

    class Dummy:
        requirements = "requirements-[base].txt"

    other += get_reqs(basepath,Dummy())

    for i in other:
        if i in to_uninstall:
            to_uninstall.remove(i)

    return to_uninstall



def install_in_current(basepath,reader):
    """
    only works in unfrozen context
    """
    this_python = sys.executable
    the_venv = sys.prefix
    if the_venv == sys.base_prefix:
        return False # will not allow global install

    subprocess.run([this_python,"-m","pip","install","-r",reader.requirements])
    #try it out
    return is_installed(basepath,reader)


def uninstall_from_current(basepath,reader):
    """only works on unfrozen context"""
    this_python = sys.executable
    packages = _get_removeable_packages(basepath,all_readers,reader)

    command = [this_python,"-m","pip","uninstall",*[f"{p.name}" for p in packages],"-y"]
    print(f"running command to uninstall: \n {' '.join(command)}")
    res = subprocess.run(command)
    if res.returncode == 0:
        return True
    else:
        return False

def install_reader(basepath,reader:object,where:INSTALL_IN):
    """allows the user to install the reader through the ui"""

    match where:
        case INSTALL_IN.CURRENT_VENV:
            res = install_in_current(basepath,reader)

        case INSTALL_IN.DEDICATED_VENV:
            res = make_dedicated_venv(basepath,reader)
            return res and is_installed(basepath,reader)

        case _:
            res = False


    return res

def uninstall_reader(basepath,reader,fr_om,kv=KEYS):
    """removes the readers dedicated venv or uninstalles it from the current venv"""

    match fr_om:
        case INSTALLED_IN.CURRENT_VENV:
            success = uninstall_from_current(basepath,reader)
            if success: 
                kv[f"is_installed-{reader.__name__}"] = False
            return 

        case INSTALLED_IN.DEDICATED_VENV:
            success = remove_venv(basepath,reader)
            if success: 
                kv[f"is_installed-{reader.__name__}"] = False
            return 

        case _:
            raise ValueError(f"fr_om is not valid: {fr_om}, acceped_options are: {INSTALLED_IN.CURRENT_VENV,INSTALLED_IN.DEDICATED_VENV}")



    


