"""should be better optimized then the first version,
    - makes reader cores
    - connects to the reader cores
    - sends commands to the reader cores
    - like:
    ```
    reader = ReaderCoreConnector(
        base_path = os.getcwd(),
        is_frozen = False,
        core_count = "4" 
    )
    reader.Speak(text="some important text") 
    reader.save_audio(text="no one is useless in this world who lightens the burdens of another",filename="dickn_s__quote.wav")
    ```




 """

import socket

import json
try:
    from helpers.bookreaders import BaseReader
except:
    from bookreaders import BaseReader
import subprocess
import sys
import time
import signal
from threading import Thread, Lock
import os


class ReaderCoreConnector(BaseReader):
    """make the readercore: which is a socket server you can use this to generate faster if you are using a weaker device,


    **Params:**
    - is_frozen: defaults to False, pass True if your app is compiled
    - core_count: str it should not exceed your physical core counts, recommended is 2
    - starting_port: defaults to 4222"""
    

    def __init__(self, *args, speaker="there was no speaker specified", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)
        try:
            self.is_frozen = kwargs.get("is_frozen",False)
            self.core_count = int(kwargs.get("core_count",1))
            self.starting_port = kwargs.get("starting_port",4222)
            self.cores = {}
            self._make_and_connect_cores()
            self.ready = True
            self.imported_ok = True
        except Exception as e:
            self.error = e



    def clean_up(self,*args,**kwargs):
        # kills the cores as soon as they free up
        self.kill_cores()


    def _force_kill(self,port):
        """forcefully terminates a core if it becomes unresponsive"""
        pid = self.cores[port]["pid"]
        os.kill(pid,signal.SIGINT)


    def restart_core(self,port):
        """kills a core and restarts it"""
        try:
            self.cores[port]["client"].close()
        except:
            pass
        self._force_kill(port)
        pid = self._make_one_core(port)
        self.cores[port]["pid"] = pid

        client = socket.socket()
        client.connect(("127.0.0.1",int(port)))
        self.cores[port]["client"] = client
        if self.cores[port]["lock"].locked():
            self.cores[port]["lock"].release()
        #should i try release the lock here?

    def kill_cores(self):
        """stops the cores from running"""
        for _ in range(0,self.core_count):
            free_core, port = self.get_core()

            free_core.sendall(json.dumps(
                {
                    "type":"terminate"
                }
            ).encode())
            response = free_core.recv(1024)
            data = json.loads(response)
            if not data.get("shutting_down"):
                self._force_kill(port)
        
        return True

    def _make_one_core(self,port):
        """makes a singular core"""
        if not self.is_frozen:
            pid = subprocess.Popen([sys.executable,"readercore.py","--port",f"{port}"])
        else:
            pid = subprocess.Popen(["readercore.exe","--port",f"{port}"])
        return pid

    def _make_and_connect_cores(self):
        """starts up some readercores"""
        self.ports = []
        self.pids = []
        for i in range(self.starting_port,self.starting_port+self.core_count):
            pid = self._make_one_core(i)
            self.ports.append(i)        
            self.pids.append(pid)
        # connecting all the cores one by one
        print(self.ports)
        for port,pid in zip(self.ports,self.pids):
            connected = False
            tries = 0
            while not connected and tries < 100:
                try:
                    client = socket.socket()
                    client.connect(("127.0.0.1",port))
                    self.cores[port] = {
                        "state":"free",
                        "lock":Lock(),
                        "client":client,
                        "pid":pid
                    }
                    print("linked to core with: ",port)
                    connected = True
                except:
                    time.sleep(2)
                    tries += 1

        return True


    def release_core(self,port):
        """sets the state of the core as free and releases the lock"""
        self.cores[port]["state"] = "free"
        self.cores[port]["lock"].release()
        print(f"set free: {port}")
        

    def get_core(self):
        free_core = None
        tries = 0
        while tries < 100:
            for port in self.ports:
                if self.cores[port]["lock"].acquire(timeout=2):
                    free_core = self.cores[port]["client"]
                    if self.cores[port]["state"] == "free":
                        print(f"using core: {port}")
                        return free_core, port 
                    else:
                        self.cores[port]["lock"].release()
            time.sleep(1)

        raise Exception("tried to get the core in get_core, 100 times, could not, exiting")


    def _Speak(self,*args,**kwargs):
        text = kwargs.get("text")
        free_core, port = self.get_core()
        free_core.sendall(json.dumps(
            {
                "text":text,
                "type":"Speak"
            }
        ).encode())
        response = free_core.recv(1024)
        data : dict = json.loads(response)
        print(data)
        self.release_core(port)
        if not data.get("success"):
            tries = kwargs.get("tries",1)
            if tries > 50:
                self.restart_core(port)
                tries = 0
                #print(".")
                #raise Exception("speak has been called 50 times, app breaking error detected")
            return self._Speak(text=text,tries=tries+1)
        return
        


    def Speak(self,*args,**kwargs):
        th = Thread(
            target=self._Speak,
            args=args,
            kwargs=kwargs
        )
        th.start()
        if kwargs.get("blocking"):
            th.join()

    def _save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        filename = kwargs.get("filename")

        free_core, port = self.get_core()
        free_core.sendall(json.dumps({
            "text":text,
            "filename":filename,
            "type":"save_audio"
        }).encode())
        response  = free_core.recv(1024)
        data = json.loads(response)
        self.release_core(port)
        if not data.get("success"):
            tries = kwargs.get("tries",1)
            if tries > 50:
                raise Exception("app breaking error, in save audio")
            time.sleep(.5)
            return self._save_audio(text=text,filename=filename,tries = tries+1)



        


    def save_audio(self,*args,**kwargs):
        th = Thread(
            target=self._save_audio,
            args=args,
            kwargs=kwargs
        )
        th.start()
        if kwargs.get("blocking"):
            th.join()




if __name__ == "__main__":
    import os
    reader = ReaderCoreConnector(
        core_count="3",
        is_frozen = False,

    )
    reader.Speak(text="Hello there")
    reader.save_audio(text="Hello General")
    reader.clean_up()