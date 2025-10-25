"""if there is no connection to the server for a give time we want to turn off the server, this behavior can be turned on or off in the appconfig.json file"""

import threading
import time
from functools import partial

class InactivityManager():

    def __init__(self,max_timeout=10*60, interval=5):
        self.last_activity = time.time()
        self.interval = interval
        self.max_timeout = max_timeout
        self.print_on = False
        self._shutdown = None
        self.enabled = False
       



    def stop(self):
        """stops the InactivityManager from tracking"""
        self.enabled = False


    def shutdown(self):
        if self._shutdown:
            self._shutdown()
        else:
            raise Exception ("Shutdown is not implemented")

    def set_shutdown_callback(self,func):
        self._shutdown = func

    def trigger(self):
        """can be called manually to update the last time you had activity"""
        
        self.last_activity = time.time()
        #print(f"updated shutdown time | current time: {self.last_activity}")

    def auto_shutdown(self):
        """checks periodically to see if your server is still getting requests, calls shutdown after we exceed a certain time limit"""
        if self.enabled:
            return
        
        self.enabled = True
        def helper():
            while self.enabled:
                time.sleep(self.interval)
                diff = time.time() - self.last_activity
                print(f"auto_shutdown is checking | closing in {self.max_timeout- diff} if no new activity")
                if (diff) > self.max_timeout:
                    self.shutdown()
                    break
        
        th = threading.Thread(target=helper,daemon=True)
        th.start()

    
    def activity_logger(self,func):
        def wrapper(*args,**kwargs):
            self.trigger()
            return func(*args,**kwargs)
        return wrapper
    
INACTIVITY_MANAGER = InactivityManager()

