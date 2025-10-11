"""checks to see if our server is running or not"""
from helpers.thepanic import Pan as pan
from urllib import request
import json

@pan.try_until(maxtries=60,timeout=1,default_value=False)
def is_server():
    """tries until it gets a connection"""
    import urllib.request
    code = (urllib.request.urlopen("http://localhost:5003/api/alive").getcode())
    if code == 200:
        return True





@pan.try_until(maxtries=10,timeout=1)
def kill_server():
    """stops the servers process"""
    r = request.urlopen("http://localhost:5003/api/killserver")
    data = json.loads(r)
    if data["status"] == "scheduled":
        print("server is shutting down")
        return True



