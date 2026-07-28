"""returns the root of the project or"""
import os
import sys


def getroot():
    if getattr(sys,"frozen",False):
        BASEPATH = sys._MEIPASS
    else:
        BASEPATH = os.path.dirname(os.path.dirname(__file__))
    return BASEPATH

if __name__ == "__main__":
    THEROOT = getroot()
    print("THIS IS ROOT:",THEROOT)