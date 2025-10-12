"""to make this more optimal for weaker pcs we are going to handle all the heavy stuff in this subprocess"""

from helpers.loadreader import load_reader,get_readers_config
from plusreaders import readers as custom_readers
from helpers.bookreaders import readers as builtin_readers
import sys
import os
import signal
import argparse


import socket
from threading import *


parser = argparse.ArgumentParser(
    prog="ReaderCore",
    description="Reads a text or creates audio from text, using the readers in the folder",
    epilog="what is this even"
)

parser.add_argument("--port",required=True)

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_PATH = sys._MEIPASS
    print(BASE_PATH)
    DEBUG = False

else:
    # Running as normal Python script
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    print(BASE_PATH)
    DEBUG = False


SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
GLOBALREADER  = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)

args = parser.parse_args()

import socket
import json

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind(("127.0.0.1",int(args.port)))
server.listen(1)

while True:
    client,adrr = server.accept()
    msg = (client.recv(1024).decode())
    data = json.loads(msg)

    if data["type"] == "Speak":
        GLOBALREADER.Speak(text=data["text"])
        client.sendall(json.dumps({"success":True}).encode())

    if data["type"] == "save_audio":
        filename = GLOBALREADER.save_audio(text=data["text"],filename=data["filename"])
        client.sendall(json.dumps({"success":filename}).encode())

    if data["type"] == "terminate":
        pid = os.getpid()
        def shutdown():
            client.sendall(json.dumps({"shutting_down":True}).encode())
            client.close()
            server.close()
            os.kill(pid,signal.SIGINT)
        shutdown()


    if data["type"] == "request_data":
        keys = data.get("keys")
        response = {}
        for key in keys:
            response[key] = GLOBALREADER.__getattribute__(key)

        client.sendall(json.dumps(response).encode())
