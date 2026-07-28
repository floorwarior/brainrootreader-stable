"""limits how often can a funtion be called """

from functools import wraps
import datetime
import time


class Throttle():


    def __init__(self):        
        self.function_history = {} # used to check when was the target function last run

    def nice(self,throttle_for,steps):
        def midlayer(func):
        
            @wraps(func)
            def wrapps(*args,**kwargs):
                last_run = self.function_history.get(func, 0)
                while (last_run + throttle_for) > datetime.datetime.timestamp(datetime.datetime.now()):
                    time.sleep(steps)
                self.function_history[func] = datetime.datetime.timestamp(datetime.datetime.now())
                return func(*args,**kwargs)
            return wrapps

        return midlayer


class KeepCool():

    def __init__(self,timeout_for,step):
        self.timeout_for = timeout_for
        self.last_run = 0
        self.step = step

    def throttle(self):
        while (self.last_run + self.timeout_for) > datetime.datetime.timestamp(datetime.datetime.now()):
            time.sleep(self.step)
        self.last_run = datetime.datetime.timestamp(datetime.datetime.now())
        return True


    def set(self):
        self.last_run = datetime.datetime.timestamp(datetime.datetime.now())


