"""to make this more optimal for weaker pcs we are going to handle all the heavy stuff in this subprocess"""

from helpers.loadreader import load_reader,get_readers_config
from plusreaders import readers as custom_readers
from helpers.bookreaders import readers as builtin_readers
from helpers.enums import ReaderCoreEnums
from helpers.throttle import KeepCool
from helpers.settings import load_app_config_v2
from helpers.get_root import getroot


from helpers.thepanic import Pan as pan
import sys

import os
import signal
import argparse
import json
import socket
from threading import *
import datetime
# block for pyinstaller to pick up needed packages
'''import helpers
import plusreaders
import readerconfigs
import pythoncom
import nltk
import numpy
import sounddevice
import win32com
import wave
import kokoro
import piper
import misaki
import language_data
import language_tags'''
# ---------------



def main():

    try:
        parser = argparse.ArgumentParser(
            prog="ReaderCore",
            description="Reads a text or creates audio from text, using the readers in the folder",
            epilog="what is this even"
        )

        parser.add_argument("--port",required=True)
        parser.add_argument("--reader",required=False)
        #parser.add_argument("--basepath",required=True)

        args = parser.parse_args()


                
        BASE_PATH = getroot()
        BRRAPPCONFIG = load_app_config_v2(BASE_PATH)


        print("readercore running from directory: ", BASE_PATH)

        if not args.reader:
            SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
        else:
            SELECTED_READER = {**custom_readers,**builtin_readers}[args.reader]

        READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
        GLOBALREADER  = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)
    

        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        throttle = BRRAPPCONFIG["subprocess"]["throttle"] 
        if throttle:
            kp = KeepCool(
                timeout_for=BRRAPPCONFIG["subprocess"]["throttle_for"],
                step=BRRAPPCONFIG["subprocess"]["throttle_step"]
            )

        server.bind(("127.0.0.1",int(args.port)))
        server.listen(1)
        server.settimeout(None)
        client,adrr = server.accept()
        while True:
            msg = (client.recv(2048*10).decode())
            data = json.loads(msg)

            if data["type"] == ReaderCoreEnums.SPEAK:
                GLOBALREADER.Speak(text=data["text"])
                client.sendall(json.dumps({"success":True}).encode())

            if data["type"] == ReaderCoreEnums.SAVE_AUDIO:
                if throttle:
                    kp.throttle()
                GLOBALREADER.save_audio(text=data["text"],filename=data["filename"])
                if throttle:
                    kp.set()
                client.sendall(json.dumps({"success":True,"filename":data["filename"]}).encode())
 
            if data["type"] == ReaderCoreEnums.TERMINATE:
                print(data["type"])
                #raise KeyboardInterrupt
                pid = os.getpid()
                def shutdown():
                    client.sendall(json.dumps({"shutting_down":True}).encode())
                    client.close()
                    server.close()
                    os.kill(pid,signal.SIGINT)
                shutdown()

            if data["type"] == ReaderCoreEnums.CLASS_METHOD:
                data_args = data.get("args")
                data_kwargs = data.get("kwargs")
                method_res = GLOBALREADER.__getattribute__(data["method"])(*data_args,**data_kwargs)
                #print(method_res)
                client.sendall(json.dumps(method_res).encode())

            if data["type"] == ReaderCoreEnums.REQUEST_DATA:
                keys = data.get("keys")
                response = {}
                for key in keys:
                    response[key] = GLOBALREADER.__getattribute__(key)

                client.sendall(json.dumps(response).encode())
    except Exception as error:
        pan.logger.info(error)

if __name__ == "__main__":
    main()

