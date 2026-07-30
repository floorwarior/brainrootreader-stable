"""
key store for simple values like
- selected_video
- playback_speed
"""



import json
from peewee import *

# An in-memory SQLite database. Or use PostgresqlDatabase or MySQLDatabase.
db = SqliteDatabase("kv.db")

class BaseModel(Model):
    """All models inherit this to share the database connection."""
    class Meta:
        database = db

class Keys(BaseModel):
    key = TextField(unique=True)
    value = TextField()

db.create_tables([Keys])
db.close()

class KVContext():
    def __init__(self,db:SqliteDatabase):        
        self.db = db

    def __enter__(self):
        self.db.connect()
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()
        


def kv_connect(fn):
    def wrapper(*args,**kwargs):
        with KVContext(db):
            res = fn(*args,**kwargs)
            return res
    return wrapper



REALKEYS = ["video","video_type","playback_speed","text_size","theme","last_visited_page","last_bookmarked_page"]
VALID_PRE = ["bookmark","last-visited","is_installed"]
DEFAULTS = {
        "video":{"value":"/static/videos/spinningfish.mp4"},
        "video_type":{"value":"video"}
    }

def is_valid_key(fn):
    def wrapper(*args,**kwargs):
        key :str= kwargs.get("key") or args[1]
        if key not in REALKEYS and not any([key.startswith(f) for f in VALID_PRE]):
            print(f"{key}: is not a valid key")
            return False
        else:
            return fn(*args,**kwargs)

    return wrapper


class Kv():


    @is_valid_key
    @kv_connect
    def __delitem__(self, key):
        item = Keys.get(Keys.key == key)
        item.delete_instance()



    @is_valid_key
    @kv_connect
    def __setitem__(self, key, value):
        Keys.insert(key=key,value=value).on_conflict(conflict_target=[Keys.key],preserve=[Keys.value]).execute()

    @is_valid_key
    @kv_connect
    def __getitem__(self, key):
        item = None
        try:
            item = [j for j in Keys.select().where(Keys.key == key)][0]
        except:
            if key in DEFAULTS:
                return DEFAULTS[key]
        return item

    @kv_connect
    def to_dict(self):
        data = {}
        for item in Keys.select():
            data[item.key] = item.value
        return data


    def to_json(self):
        return json.dumps(self.to_dict())


KEYS = Kv()

if __name__ == "__main__":
    keyz = Kv()
    keyz["theme"] = "shrek"
    keyz["theme"] = "pink"
    keyz["text_size"] = "3xl"
    keyz["last_visited_page"] = "75"
    keyz["last_bookmarked_page"] = "67"
    print(keyz["is_installed-kokoro"])


   

    print(keyz.to_dict())
