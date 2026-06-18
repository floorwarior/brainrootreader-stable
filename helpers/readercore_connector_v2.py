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
from secrets import token_urlsafe

from queue import PriorityQueue
import json
try:
    from helpers.bookreaders import BaseReader
except:
    from bookreaders import BaseReader
import subprocess
from threading import Event
import sys
import time
import signal
from threading import Thread, Lock,Event
import os

from dataclasses import dataclass
from time import sleep,time


from helpers.loadreader import load_reader
from helpers.bookreaders import readers as builtin_readers
from plusreaders import readers as custom_readers





class LazyCompareable():


    def __init__(self,prio):
        self.prio = prio


    def is_same_as(self,other):
        return self.__dict__ == other.__dict__

    def __gt__(self, other):
        if not isinstance(other,LazyCompareable):
            raise ValueError("Not comperable")
        return self.prio > other.prio
    

    def __eq__(self, value):
        return self.prio == value


    def __lt__(self,other):
        if not isinstance(other, LazyCompareable):
            raise ValueError("Not Comperable")
        return self.prio < other.prio

@dataclass(eq=False)
class SpeakTask(LazyCompareable):
    type: str
    text :str
    prio : int = 1


@dataclass(eq=False)
class SaveAudioTask(LazyCompareable):
    type : str
    text : str
    filename : str 
    prio: int


class KillCores(LazyCompareable):
    type : str = "kill_cores"
    prio : int = 0



class ReaderCoreConnector(BaseReader):
    """make the readercore: which is a socket server you can use this to generate faster if you are using a weaker device,


    **Params:**
    - is_frozen: defaults to False, pass True if your app is compiled
    - core_count: str it should not exceed your physical core counts, recommended is 2
    - starting_port: defaults to 4222
    - forced_reader: you can pass a readers name dirrectly this will overwrite the readerorder    
    """
    

    def __init__(self, *args, speaker="there was no speaker specified", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)
        try:
            self.is_frozen = kwargs.get("is_frozen",False)
            self.core_count = int(kwargs.get("core_count",1))
            self.starting_port = kwargs.get("starting_port",4222)
            self.forced_reader = kwargs.get("forced_reader",False)
            self.cores = {}
            self._make_and_connect_cores()
            self.ready = True
            self.imported_ok = True

            self.priority_lookup = []
            self.priority_queue = PriorityQueue()
            
            self.threads = {}
            self.exit_event = Event()
            for z in range(0,self.core_count):
                self._main_loop()
        except Exception as e:
            print("READERCORE ERROR:",e)
            self.error = e

    def clean_up(self,*args,**kwargs):
        self.kill_cores()
   
    def _force_kill(self,port):
        """forcefully terminates a core if it becomes unresponsive"""
        pid = self.cores[port]["pid"]
        self.priority_queue.empty()
        os.kill(pid,signal.SIGINT)



    def on_queue_change(self,callback):
        self._on_queue_change = callback

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
            #IDEA: make this load form the venv correcponding to the reader not directly like bellow
            if not self.forced_reader:
                SELECTED_READER = load_reader(base_path=self.base_path,custom_readers=custom_readers,builtin_readers=builtin_readers)
            else:
                SELECTED_READER = {**custom_readers,**builtin_readers}[self.forced_reader]

            dedicated_venv = os.path.join(self.base_path,f".{SELECTED_READER.__name__.lower()}-venv")

            if os.path.exists(dedicated_venv):
                command = [os.path.join(dedicated_venv,"Scripts","python.exe"),"readercore.py","--port",f"{port}"]
                if self.forced_reader:
                    command += ["--reader",self.forced_reader]

                pid = subprocess.Popen(command)
                print(f"[SPECIAL VENV DOES EXISTS: {dedicated_venv}]")
            else:
                print(f"[SPECIAL VENV DOES NOT EXISTS: {dedicated_venv}]")
                command = [sys.executable,"readercore.py","--port",f"{port}"]
                if self.forced_reader:
                    command += ["--reader",self.forced_reader]
                pid = subprocess.Popen(command)
            #pid = subprocess.Popen([sys.executable,"readercore.py","--port",f"{port}"])
        else:
            command = ["readercore.exe","--port",f"{port}"]
            if self.forced_reader:
                command += ["--reader",self.forced_reader]
            pid = subprocess.Popen(command)
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
                    sleep(2)
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
                        self.cores[port]["state"] = "busy"
                        return free_core, port 
                    else:
                        self.cores[port]["lock"].release()
            sleep(.1)

        raise Exception("tried to get the core in get_core, 100 times, could not, exiting")


    def on_Speak(self,*args,**kwargs):
        pass

    
    def _on_Speak(self,*args,**kwargs):
        if self.on_Speak:
            self.on_Speak(*args,**kwargs)


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
                raise Exception("speak has been called 50 times, app breaking error detected")
            return self._Speak(text=text,tries=tries+1)
       
        self._on_Speak(*args,**kwargs)

    
    def _on_queue_change(self,*args,**kwargs):
        current_item = kwargs.get("current_item")
        queue_size = kwargs.get("queue_size")
        self.priority_lookup.remove(current_item.__dict__)
        print(f"current task: {current_item}, queue_size: {queue_size}")


    def _main_loop(self):
        def helper():
            while True:
                if self.priority_queue.not_empty:
                    #print(self.priority_queue)
                    _,current_task = self.priority_queue.get()
                    self._on_queue_change(
                        current_item=current_task,
                        queue_size = self.priority_queue.qsize()
                    )
                    match current_task.type:
                        case "Speak":
                            self._Speak(text=current_task.text)

                        case "save_audio":
                            self._save_audio(text=current_task.text,filename=current_task.filename)

                        case "kill_cores":
                            self.kill_cores()
                    
                elif self.exit_event.is_set():
                    break

                else:
                    sleep(.1)
        th_id = token_urlsafe(12)
        self.threads[th_id] = Thread(target=helper)
        self.threads[th_id].start()

    def Speak(self,*args,**kwargs):
        text=kwargs.get("text")
        speak_task = SpeakTask(
                text=text,
                type="Speak",
                prio=1
            ) 
        
        if speak_task.__dict__ in self.priority_lookup:
            return
        
        self.priority_queue.put(item=(
            1,speak_task
        )
        )

        self.priority_lookup.append(speak_task.__dict__)

        return



    def on_save_audio(self, *args, **kwargs):
        print(f"Converted: {kwargs.get('filename')}")


    def _on_save_audio(self,*args,**kwargs):
        if self.on_save_audio:
            self.on_save_audio(*args,**kwargs)

    def _save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        filename = kwargs.get("filename")
        if not kwargs.get("free_core") and not kwargs.get("port"):
            free_core, port = self.get_core()
        else:
            free_core = kwargs.get("free_core")
            port = kwargs.get("port")

        free_core.sendall(json.dumps({
            "text":text,
            "filename":filename,
            "type":"save_audio"
        }).encode())
        response  = free_core.recv(1024)
        print(response)
        data = json.loads(response)
        self.release_core(port)
        if not data.get("success"):
            tries = kwargs.get("tries",1)
            if tries > 50:
                raise Exception("app breaking error, in save audio")
            sleep(.5)
            return self._save_audio(text=text,filename=filename,tries = tries+1)
        
        self._on_save_audio(*args,**kwargs)






    def save_audio(self,*args,**kwargs):
        #print(self.cores)
        text = kwargs.get("text")
        filename = kwargs.get("filename")
        priority = kwargs.get("priority",2)

        tsk = SaveAudioTask(
            prio=priority,
            text=text,
            filename=filename,
            type="save_audio"
        )
        if tsk.__dict__ in self.priority_lookup:
            return
        else:
            self.priority_lookup.append(tsk.__dict__)

        self.priority_queue.put(item=(priority,tsk))
        return 


if __name__ == "__main__":
    import os
    reader = ReaderCoreConnector(
        core_count="3",
        is_frozen = False,

    )

    
    reader.save_audio(text="what what what what what what",filename="whatwhatwhatwhatwhatwhatwhat1.wav",priority=2)
    reader.save_audio(text="what what what what what what",filename="whatwhatwhatwhatwhatwhatwhat2.wav",priority=3)
    reader.save_audio(text="what what what what what what",filename="whatwhatwhatwhatwhatwhatwhat3.wav",priority=4)
    reader.save_audio(text="what what what what what what",filename="whatwhatwhatwhatwhatwhatwhat4.wav",priority=5)
    reader.save_audio(text="what what what what what what",filename="whatwhatwhatwhatwhatwhatwhat5.wav",priority=6)
    reader.Speak(text="This should play pretty much first or second")
   