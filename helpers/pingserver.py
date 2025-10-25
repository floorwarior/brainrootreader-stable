"""checks to see if our server is running or not"""
from helpers.thepanic import Pan as pan
from urllib import request
import json
import urllib.request


@pan.try_until(maxtries=60,timeout=1,default_value=False,supress=True)
def is_server():
    """tries until it gets a connection"""
    code = (urllib.request.urlopen("http://localhost:5003/api/alive").getcode())
    if code == 200:
        return True



def health_check(timeout=5):
    """checks if the server is responsive still, this should be only used after we are sure the server worked initially"""

    try:
        code = (urllib.request.urlopen(url="http://localhost:5003/api/alive",timeout=timeout).getcode())
        if code == 200:
            return True
    except:
        return False





@pan.try_until(maxtries=10,timeout=1,supress=True,default_value=True)
def kill_server():
    """stops the servers process"""
    code = request.urlopen("http://localhost:5003/api/killserver").getcode()
    if code == 200:
        print("server is shutting down")
        return True





