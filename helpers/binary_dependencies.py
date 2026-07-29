import shutil
import os

def is_binary_available(binary):
    """checks to see if a binary is installed or not"""
    exists = shutil.which(binary)
    #print(f"Exists in {exists}")
    if exists:
        return exists and os.access(exists,os.X_OK)

    return False

class BinaryDependencyNotFound(Exception):
    pass


class BinaryDependency():

    def __init__(self,name,link):
        self.name = name
        self.link = link

    def is_available(self):
        return is_binary_available(self.name)
 
    def geterror(self):
        return BinaryDependencyNotFound(f"'{self.name}' is not installed or not part of your Path, install it from here: {self.link}")


# Binary Deps
SOX = BinaryDependency("sox","https://sourceforge.net/projects/sox/")
ESPEAK_NG = BinaryDependency("espeak-ng","https://github.com/espeak-ng/espeak-ng")
FFMPEG = BinaryDependency("ffmpeg","https://www.ffmpeg.org/download.html")
