"""routes that are meant to be used via fetch and return json answers"""
from flask import Blueprint, render_template, abort,request,jsonify
from jinja2 import TemplateNotFound
from helpers.kv import KEYS
from helpers.settings import save_config_file,load_app_config_v2,edit_field,get_field
from helpers.install_tools import is_installed,install_reader,INSTALL_IN,uninstall_reader
from helpers.get_root import getroot
from helpers.settings import BASE_PATH,BRRAPPCONFIG
from helpers.settings import all_readers
from helpers.makebrr import add_card,add_note,update_card,update_note,get_notes,get_cards,remove_note,remove_card,get_card
from helpers.thepanic import Pan


api_v2 = Blueprint(name="api_v2",import_name=__name__,template_folder='templates')


@api_v2.route("/")
def base():
    return "test"


@api_v2.route("/getkey")
def get_key():
    key = request.args.get("key")
    try:
        return jsonify(KEYS[key].value)
    except AttributeError:
        return jsonify(None)

@api_v2.route("/setkey",methods=["POST"])
def set_keys():
    new_key = request.get_json()
    print(new_key)
    KEYS[new_key["key"]] = new_key["value"]

    return jsonify({"result":True,"changed":new_key})

@api_v2.route("/getkeys")
def get_keys():
    return jsonify(KEYS.to_dict())



@api_v2.route("/config")
def get_config():
    return jsonify(BRRAPPCONFIG)


@api_v2.route("/setconfig",methods=["POST"])
def set_config():
    """accepts json like:
    ```
        {
            "dotnotation":"app.port",
            "value":5101
        }    
    ```
    """
    data = request.get_json()
    dotnotation = data["dotnotation"]
    value = data["value"]
    try:  
        success = edit_field(BRRAPPCONFIG,dotnotation,value)
        save_config_file(BRRAPPCONFIG,BASE_PATH)
        return jsonify({"success":success})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)})

@api_v2.route("/setconfigs",methods=["POST"])
def set_configs():
    """accepts a json like this
    ```
    data = {
        "app.port":5002,
        "app.host":"localhost"
    }
    ```
    """
    data = request.get_json()
    suc = []
    try:
        for key,value in data.items():
            success = edit_field(BRRAPPCONFIG,key,value)
            suc.append(success)

        save_config_file(BRRAPPCONFIG,BASE_PATH)
        return jsonify({"success":all(suc)})

    except Exception as e:
        return jsonify({"success":False,"error":str(e)})


@api_v2.route("/getconfig/<dotnotation>")
def get_config_(dotnotation):
    return jsonify(get_field(BRRAPPCONFIG,dotnotation))

@api_v2.route("/is_installed",methods=["POST"])
def check_if_installed():
    data = request.get_json()
    print(data)
    reader_name = data["reader"]
    reader = all_readers[reader_name]
    return jsonify(
        is_installed(BASE_PATH,reader,try_cache=False)
    )


@api_v2.route("/install_reader",methods =["POST"])
def installs_reader():
    data = request.get_json()
    print(data)
    reader_name = data["reader"]
    reader = all_readers[reader_name]
    where = data["where"]
    return jsonify(install_reader(BASE_PATH,reader=reader,where=where))



@api_v2.route("/uninstall_reader",methods=["POST"])
def uninstalls_reader():
    data = request.get_json()
    print(data)
    reader_name = data["reader"]
    reader = all_readers[reader_name]

    fr_om = data["from"]
    return jsonify(uninstall_reader(BASE_PATH,reader,fr_om))




@api_v2.route("/setnote",methods=["POST"])
def set_note():
    data = request.get_json()
    note = data["note"]
    page = data["page"]
    book_id = data["book_id"]
    try:
        add_note(
            page=page,
            note=note,
            book_id=book_id
        )
        return jsonify(True)
    except:
        return jsonify(False)

@api_v2.route("/updatenote",methods=["POST"])
def updatenote():
    data = request.get_json()
    note = data["note"]
    note_id = data["note_id"]

    try:
        update_note(
            note_id=note_id,
            new_note=note
        )
        return jsonify(True)
    except:
        return jsonify(False)
    


@api_v2.route("/getnotes",methods=["POST"])
def getnotes():
    """returns the notes for a specific page of a book"""
    data = request.get_json()

    book_id = data["book_id"]
    page = data["page"]


    res = []
    try:
        for note in get_notes(page=page,book_id=book_id):
            res.append(
                {   "note_id":note.id,
                    "page":note.page,
                    "note":note.note,
                    "book_id":note.book_id
                }
            )
    except Exception as e:
        print(e)
        return False
    
    return res


@api_v2.route("/deletenote",methods=["POST"])
def delnote():
    data = request.get_json()
    try:
        note_id = data["note_id"]
        return jsonify(remove_note(note_id))
    except:
        return jsonify(False)
    



@api_v2.route("/setcard",methods=["POST"])
def setcard():
    try:
        data = request.get_json()
        print(data)
        add_card(
            page=data["page"],
            book_id=data["book_id"],
            question=data["question"],
            answer=data["answer"]
        )
        return jsonify(True)

    except Exception as e:
        print(e)
        return jsonify(False)
    


@api_v2.route("/updatecard",methods=["POST"])
def updatecard():
    try:
        data = request.get_json()
        print(data)
        update_card(
            card_id=data["id"],
            new_question=data["question"],
            new_answer=data["answer"]
        )
        return jsonify(True)
    
    except Exception as e:
        #print(e)
        return jsonify(str(e))


@api_v2.route("/deletecard",methods=["POST"])
def delcard():
    try:
        data = request.get_json()
        print(data)
        r = remove_card(int(data["card_id"]))
        print(r)
        return jsonify(str(r))
    except Exception as e:
        print(e)
        return jsonify(False)
    

@api_v2.route("getcards",methods=["POST"])
def get_the_cards():
    try:
        data = request.get_json()
        print(data)
        tmp = []
        for c in get_cards(page=data["page"],book_id=data["book_id"]):
            tmp.append({"question":c.question,"answer":c.answer,"page":c.page,"book_id":c.book_id,"id":c.id})
        return jsonify(tmp)
    except Exception as e:
        Pan.logger.log(level=30,msg=str(e))
        return jsonify(False)
    


@api_v2.route("/getcard")
def getcard():
    try:
        card_id = request.args.get("id")
        return get_card(card_id)

    except Exception as e:
        return {"success":False,"error":str(e)} , 500



@api_v2.route("/clear_queue")
def clear_queue():
    """removes all items from the queue of the reader if it is type readercore"""
    GLOBALREADER = getattr(globals,"GLOBALREADER")
    ReaderCoreConnector = getattr(globals,"ReaderCoreConnector")
    if isinstance(GLOBALREADER,ReaderCoreConnector):
        GLOBALREADER.clear_queue()
        return jsonify({"success":True}),200

    return jsonify({"success":False}),500
