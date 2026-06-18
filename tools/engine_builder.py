"""
allows you to pin: python version, requirements
and make a dropable engine that is ready to be used with the TTSEngineConnector
both the readerengineconnector and the readercoreconnector work by the same api they are interchangeable
but the enginecore differs in that its self contained and takes no config or other arguments, it also ships its own python version
rather then the one of BRR
"""

import subprocess
import importlib
import os

from typing import Literal
from jinja2 import Template,Environment,FileSystemLoader

from helpers.loadreader import get_readers_config


class EngineBuilder():


    def __init__(self,reader,requirements,base_path):
        self.reader :str= reader
        self.requirements = requirements
        self.base_path = base_path
        self.config = get_readers_config(readername=reader,base_path=self.base_path)
        self.py_filename = f"readerengine_{self.reader.lower().replace('-','_')}.py"
        self.py_file_full_path = os.path.join(self.base_path,"tools","engine_build",self.py_filename)


    def make_build_py_file(self):
        """makes a python files with the jinja tempaltes that is ready to be exported"""
        config = "{" + "".join([f'"{key}":"{val}"' for key,val in self.config.items()]) + "}"


        # Tell Jinja2 where your template file is located
        env = Environment(loader=FileSystemLoader(os.path.join(self.base_path,"tools")))

        # Load the template
        template = env.get_template("readerengine.py")

        # Render it with variables
        output = template.render(
            requirements = self.requirements,
            _config = config,
            _reader = self.reader
        )

        with open(os.path.join(self.base_path,"tools","engine_build",self.py_filename),"w") as new_dud:
            new_dud.write(output)





    def build(self):
        """runs python.exe -m nuitka <pyfilesname>"""
        self.make_build_py_file()
        #subprocess.run(["python","-m","nuitka","generated_py_file.py"])
        subprocess.run(["pyinstaller",os.path.join(self.base_path,"tools","readerengine.spec")])

if __name__ == "__main__":
    EngineBuilder(
        reader="KokoroReader",
        requirements=importlib.import_module("kokoro").requires
    ).build()

