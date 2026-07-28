from heapq import heapify,heappop,heappush
from contextlib import contextmanager
from threading import Lock
import datetime
from time import sleep
from queue import Empty

class TaskQueue():

    def __init__(self):
        self.task_list = [] # [(0,Task())]
        self.lock = Lock()
        heapify(self.task_list)

    @contextmanager
    def use_lock(self):
        acquired = self.lock.acquire(timeout=2) 
        try:
            if acquired:
                yield 
            else:
                raise Exception("The lock is busy, could not aquire")
                
        finally:
            self.lock.release()



    def put(self,item):
        """adds a new task"""
        with self.use_lock():
            heappush(self.task_list,item)
            #print(self.task_list)


    def get(self,timeout=0,block=None):
        """gets the next task, waits at least timeout seconds if the tasklist is empty, raises Empty exception if there is no task to execute"""
        entered = datetime.datetime.timestamp(datetime.datetime.now())
        if block:
            while not self.task_list and (datetime.datetime.timestamp(datetime.datetime.now()) - entered) <= timeout:
                sleep(.1)
        with self.use_lock():
            if len(self.task_list) != 0:
                task = heappop(self.task_list)
                return task            
        raise Empty


    def clear(self):
        """removes all items from the tasklist"""
        with self.use_lock():
            self.task_list = []


    def is_empty(self):
        with self.use_lock():
            return len(self.task_list) == 0


    def get_size(self):
        with self.use_lock():
            return len(self.task_list)




  