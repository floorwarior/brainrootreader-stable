"""connects to the readercore, with multiprocess the speed of conversion should be generally a lot faster"""
import socket
from helpers.bookreaders import BaseReader
import subprocess
import threading
import os
import json
import sys
from time import sleep

class ReaderCoreConnector(BaseReader):
    """can be used in the place of any Reader class, returns the same stuff, spans core_count number of readercores, can be usefull if you have more then
    one cores and want to generate data faster
    """

    def __init__(self, *args,  speaker="ReaderCore", **kwargs):
        super().__init__(*args,speaker,**kwargs)
        self.starting_port = 4222
        self.core_count = int(kwargs.get("core_count"))
        self.is_frozen = kwargs.get("is_frozen")
        self.base_path = kwargs.get("base_path")
        self.cores = []
        
        self.origin = "readercore"
        self.order_66()
        if self._make_cores():
            self.imported_ok = True
            self.ready = True
        self.output_ending = self.get_reader_attributes(keys=["output_ending"]).get("output_ending")

    def order_66(self):
        """terminates all the reader cores"""
        for i in self.cores:
            terminated = False
            while not terminated:
                try:
                    client = socket.socket()
                    client.settimeout(None)
                    client.connect(("127.0.0.1",i))
                    client.send(json.dumps({"type":"terminate"}).encode())
                    response = client.recv(1024)
                    data = json.loads(response)
                    if data["shutting_down"] == True:
                        print(f"shutting down reader core on port: {i}")
                        terminated = True
                        client.close()
                    else:
                        client.close()
                except Exception as e:
                    sleep(.1)
                    pass



    def _make_cores(self):
        """starts up some readercores"""
        for i in range(self.starting_port,self.starting_port+self.core_count):
            if not self.is_frozen:
                subprocess.Popen([sys.executable,"readercore.py","--port",f"{i}"])
            else:
                subprocess.Popen(["readercore.exe","--port",f"{i}"])
            self.cores.append(i)
        return True


    def connect_one_core(self):
        connected =False
        tries = 0
        while not connected and tries < 100:
            for i in self.cores:
                try:
                    client = socket.socket()
                    client.settimeout(None)
                    client.connect(("127.0.0.1",i))
                    connected = True
                    print(f"connected to core: {i}")
                    port = i
                    return client , port
                except Exception as e:
                    tries += 1
                    sleep(0.1)
                    print(e)
                    #print(f"{i} is busy trying next core")

        raise BaseException("no cores connected or detected")


    def Speak(self,*args,**kwargs):
        speaker_thread = threading.Thread(target=self._Speak,args=args,kwargs=kwargs)
        speaker_thread.start()
        if kwargs.get("blocking"):
            speaker_thread.join()


    def clean_up(self):
        self.order_66()


    def _Speak(self,*args,**kwargs):
        thecore , port = self.connect_one_core()
        process_this = {
            "type":"Speak",
            "text":kwargs.get("text")
        }
        thecore.sendall(json.dumps(process_this).encode())

        response = thecore.recv(1024)
        data = json.loads(response)
        if data["success"] == True:
           
            result = True
        else:
            print(data["error"])
            result = False

        thecore.close()
        print(f"closend connection to: {port}")


        return result

    def get_reader_attributes(self,keys:list):
        """asks the reader core whatever attruibute"""
        thecore,port = self.connect_one_core()
        thecore.send(json.dumps({"type":"request_data","keys":keys}).encode())
        response = thecore.recv(1024)
        data = json.loads(response.decode())
        thecore.close()
        print(f"closed connection to core with port: {port}")
        return data

    def save_audio(self,*args,**kwargs):
        thethread = threading.Thread(target=self._save_audio,args=args,kwargs=kwargs)
        thethread.start()
        if kwargs.get("blocking"):
            thethread.join()

    def _save_audio(self,*args,**kwargs):
        thecore,port = self.connect_one_core()
        process_this = {
            "type":"save_audio",
            "text":kwargs.get("text"),
            "filename":kwargs.get("filename")
        }

        thecore.sendall(json.dumps(process_this).encode())
        response = thecore.recv(1024)
        data : dict = json.loads(response)
        print(f"converted file: {data.get('filename')}")
        #print(data["success"])
        thecore.close()
        print(f"closed connection to core with port: {port}")
        return kwargs.get("filename")


