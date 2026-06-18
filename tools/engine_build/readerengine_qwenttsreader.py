"""template for generating a readerengine"""

from helpers.bookreaders import readers as builtin_readers

from helpers.thepanic import Pan as pan
import sys
import os
import signal
import argparse
import json
import socket
from threading import *




def main():
    try:
        parser = argparse.ArgumentParser(
            prog="ReaderEngine",
            description="Reader with a pinned reader holds its own",
        )

        parser.add_argument("--port",required=True)
        #parser.add_argument("--basepath",required=True)

        args = parser.parse_args()


        

        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            BASE_PATH = sys._MEIPASS
            print(BASE_PATH)


        else:
            # Running as normal Python script
            BASE_PATH = os.path.abspath(os.path.dirname(__file__))
            print(BASE_PATH)



        print("readercore running from directory: ", BASE_PATH)


        SELECTED_READER = builtin_readers["QwenTTSReader"]
        READERS_CONFIG = {"speaker":"Ryan"}
        GLOBALREADER  = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)

        


        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        server.bind(("127.0.0.1",int(args.port)))
        server.listen(1)
        server.settimeout(None)
        client,adrr = server.accept()
        while True:
           
            msg = (client.recv(2048*10).decode())
            data = json.loads(msg)

            if data["type"] == "Speak":
                GLOBALREADER.Speak(text=data["text"])
                client.sendall(json.dumps({"success":True}).encode())

            if data["type"] == "save_audio":
                GLOBALREADER.save_audio(text=data["text"],filename=data["filename"])
                client.sendall(json.dumps({"success":True,"filename":data["filename"]}).encode())
 
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
    except Exception as error:
        pan.logger.info(error)

if __name__ == "__main__":
    main()
