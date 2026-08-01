import subprocess
import os
import threading
import signal
import sys
from helpers.settings import BASE_PATH,BRRAPPCONFIG,load_app_config_v2
from helpers.makebrr import NotesHandler,CardHandler,PageImageHandler,PageTextHandler
from helpers.loadreader import all_readers
from helpers.install_tools import is_installed,installed_where,INSTALLED_IN
from helpers.thepanic import Pan


from helpers.themeing import THEMES,Theme
from api.api import api_v2
from helpers.kv import KEYS

loading_window_handle = None
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    ISFROZEN = True
    print(BASE_PATH)
    DEBUG = False
    if BRRAPPCONFIG["startup"]["loading_window"] and not BRRAPPCONFIG["shutdown"]["auto_shutdown"]:
       loading_window_handle = subprocess.Popen(["loadingwindow.exe"]).pid


else:
    # Running as normal Python script
    ISFROZEN = False
    print(BASE_PATH)
    DEBUG = BRRAPPCONFIG["app"]["debug"]
    CURRENT_PYTHON = sys.executable
    if BRRAPPCONFIG["startup"]["loading_window"] and not BRRAPPCONFIG["shutdown"]["auto_shutdown"]:
        loading_window_handle = subprocess.Popen([CURRENT_PYTHON,os.path.join(BASE_PATH,"loadingwindow.py")]).pid



from flask import Flask
from flask import request,redirect,url_for,render_template,jsonify,send_file
from werkzeug.utils import secure_filename
from flask import send_from_directory
import nltk

nltk_folder_path = os.path.join(BASE_PATH,"nltk_data")

nltk.download("punkt",download_dir=nltk_folder_path)
nltk.download("punkt_tab",download_dir=nltk_folder_path)
nltk.data.path.append(nltk_folder_path)

# this block is for pyinstaller to pick up the files correctly, you can comment this out if you are not building only using the app
'''import helpers
import engineio
import plusreaders 
import readerconfigs
import pypdf
import piper
import pythoncom
import numpy
import sounddevice
import win32com
import wave
import engineio.async_drivers
import bs4
import ebooklib
from ebooklib import epub
import zipfile
import PIL 
import pytesseract
import socketio
import docx
import flask_socketio
import kokoro
import misaki # kokoros dependency
import language_data # misakies dependency
import language_tags # misakies dependency
import spacy
import spacy_legacy 
import spacy_curated_transformers
import en_core_web_sm
import loguru'''
#from TTS.api import TTS
# -- -- -- -- -- -- -- 

from helpers.book_converter import return_cache,get_booknames,make_permanent_by_page
from helpers.generalttsreader import ReadBook
from helpers.loadreader import load_reader, get_readers_config
from plusreaders import readers as custom_readers
from helpers.bookreaders import readers as builtin_readers
from helpers.store import VoiceStorePiper,VoiceStoreKokoro
from helpers.readercore_connector_v2 import ReaderCoreConnector
from helpers.autoshutdown import INACTIVITY_MANAGER
from helpers.increment_port import get_next_port


from flask_socketio import SocketIO


APPTHEME : Theme =  THEMES[BRRAPPCONFIG["style"]["theme"]]
SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
INACTIVITY_MANAGER.max_timeout = int(BRRAPPCONFIG["shutdown"]["shutdown_after"])
INACTIVITY_MANAGER.interval = 20


if BRRAPPCONFIG["app"]["audio_method"] == "threading":
    GLOBALREADER = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)

elif BRRAPPCONFIG["app"]["audio_method"] == "subprocess":
    GLOBALREADER  = ReaderCoreConnector(
        core_count = BRRAPPCONFIG["subprocess"]["core_count"],
        is_frozen = ISFROZEN,
        base_path = BASE_PATH
    )

start_port = get_next_port(4222,int(BRRAPPCONFIG["subprocess"]["core_count"]))
_ = next(start_port)

def re_initialize_reader():
    """sets a new global reader if there is a settings change"""
    global GLOBALREADER,BRRAPPCONFIG,ISFROZEN,BASE_PATH,READERS_CONFIG,SELECTED_READER,start_port
    starting_port = next(start_port)
    try:
        BRRAPPCONFIG = load_app_config_v2(BASE_PATH)
        INACTIVITY_MANAGER.max_timeout = int(BRRAPPCONFIG["shutdown"]["shutdown_after"]) 

        if BRRAPPCONFIG["app"]["audio_method"] == "subprocess":
            GLOBALREADER.clean_up()
            GLOBALREADER  = ReaderCoreConnector(
                core_count = BRRAPPCONFIG["subprocess"]["core_count"],
                is_frozen = ISFROZEN,
                base_path = BASE_PATH,
                starting_port = starting_port
            )


        elif BRRAPPCONFIG["app"]["audio_method"] == "threading":
            SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
            READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
            GLOBALREADER.clean_up()
            GLOBALREADER = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)
        return True
    except Exception as e:
        Pan.logger.log(level=20,msg=str(e))
        return False

def shutdown():
    """stops the server from running"""
    GLOBALREADER.clean_up()
    if loading_window_handle:
        try:
            os.kill(loading_window_handle,signal.SIGINT)
        except OSError:
            pass
    this = os.getpid()
    os.kill(this,signal.SIGINT)

INACTIVITY_MANAGER._shutdown = shutdown


print("this is basepath:",BASE_PATH)
app = Flask(__name__,template_folder=os.path.join(BASE_PATH,BRRAPPCONFIG["app"]["template_folder"]),static_folder=os.path.join(BASE_PATH,"static"))
app.register_blueprint(api_v2,url_prefix="/api_v2")


@app.context_processor
def inject_keys():
    return {"KEYS":KEYS}


@app.context_processor
def inject_books():
    books = get_booknames(basepath=BASE_PATH)
    return {"books":books,"int":int}



app.config["UPLOAD_FOLDER"] = os.path.join(BASE_PATH,"uploads")
socketed_app = SocketIO(app=app,async_mode="threading")

@app.route("/")
def home():
    #books = get_booknames(basepath=BASE_PATH)
    return render_template(APPTHEME.home)




@app.route("/api/downloadvoicemodel/<voice>")
def download_voice_dirrectly(voice=None):
    if not voice:
        return "no voice specified"    
    piper_voice_store = VoiceStorePiper(
    name="Piper",
    base_path=BASE_PATH,
    model_folder_foldername="pipermodels",
    baseendpoint="https://huggingface.co/rhasspy/piper-voices/resolve/main/",
    voicesendpoint="https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
    )
    kokoro_voice_store = VoiceStoreKokoro(
        name="Kokoro",
        base_path=BASE_PATH,
        model_folder="kokoromodels",
    )


    stores = {piper_voice_store.name:piper_voice_store,
              kokoro_voice_store.name:kokoro_voice_store}
    # get the correct store to call
    reader = request.args.get("reader")

    stores[reader].download_voice(voice)
    return jsonify({
        "success":True,
        "downloaded":voice
    })



@app.route("/uploads/<path:name>")
def uploads_exposed(name):
    """used for opening a pdf to a specific page"""
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], name, as_attachment=False
    )



@app.route("/voicebag/")
def voicebag():
    """allows the user to download all the voices for readers like piper"""
    piper_voice_store = VoiceStorePiper(
        name="Piper",
        base_path=BASE_PATH,
        model_folder_foldername="pipermodels",
        baseendpoint="https://huggingface.co/rhasspy/piper-voices/resolve/main/",
        voicesendpoint="https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
    )
    return render_template(APPTHEME.voicebag,voicestores=[piper_voice_store])


@app.route("/api/reload_app",methods=["POST"])
def reload_app():
    """reloads the appconfig and also reloads the reader if there are any changes it applies them"""
    re_initialize_reader()
    return jsonify(True)


@app.route("/settings",methods=["GET"])
def settings():
    _all_readers = all_readers(custom_readers,builtin_readers).values()
    installed = []
    not_installed = []

    full_reload = request.args.get("full_reload")
    if full_reload:
        re_initialize_reader()

    for reader in _all_readers:
        if is_installed(BASE_PATH,reader,try_cache=not full_reload):
            installed.append(reader)
        else:
            not_installed.append(reader)
    installed_there = {}
    for reader in installed:
        type_of_install,where = installed_where(BASE_PATH,reader)
        installed_there[reader.__name__] = {
            "where":where,
            "type_of_install":type_of_install
            }


    data = {
        "INSTALLED_IN":INSTALLED_IN,
        "selected_reader":GLOBALREADER,
        "readers":_all_readers,
        "installed_readers":installed,
        "not_installed":not_installed,
        "installed_there":installed_there,
        "config":BRRAPPCONFIG,
    }
    return render_template(APPTHEME.settings,**data)



@app.route("/deletebook/",methods=["POST","GET"])
@app.route("/deletebook/<book>",methods=["POST","GET"])
def delete_book(book=None):
    """removes the book and its contents from the system"""
    if not  book:
        return "No Book specified"
    rd = ReadBook(
        reader_=GLOBALREADER,
        safe_bookname=book,
        base_path_=BASE_PATH
    )
    if rd.delete_book():
        return redirect(url_for("home"))
    else:
        return "Error your book was not deleted"

@app.route("/testimage",methods=["POST","GET"])
def test_image_quality():
    """
    **Tests the image to convert from**
    - opens camera stream on the image and tests it
    """
    return "Feature Discontinued",410
    from helpers.book_converter import get_booknames
    return render_template(APPTHEME.test_image_quality)


@app.route("/testnewroutes")
def check_new_routes():
    """testing the new route layouts here"""
    #from helpers.book_converter import get_booknames
    #books = get_booknames(basepath=BASE_PATH)
    return render_template("templates/base.html")


@app.route("/convert",methods=["POST"])
def convert_book():

    print(request.form.to_dict())
    print(request.files["book"])
    book = request.files.get("book")

    print("[ THIS IS UPLOAD FOLDER]: ",app.config["UPLOAD_FOLDER"])

    book.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(book.filename)))
    if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(book.filename))):
        print("file does exist")
    else:
        print("file was never saved")

    res,safe_bookname = make_permanent_by_page(book=secure_filename(book.filename),basename=BASE_PATH)
    #print(res)
    return redirect(url_for("read_book_",book=safe_bookname))



@app.route("/addvideo",methods=["GET"])
def add_video():
    """allows the user to add any video to be played by the app
    """
    return redirect(url_for("settings"))
    if request.method == "POST":
        from helpers.videos import upload_video,add_video_link
        video = request.files.get("video",None)
        videolink = request.form.get("videolink")
        if video:
            safe_video_name = secure_filename(video.filename)
            video.save(dst = os.path.join(app.config["UPLOAD_FOLDER"],safe_video_name))
            upload_video(base_path=BASE_PATH,videoname=safe_video_name)
        if videolink:
            add_video_link(base_path=BASE_PATH,new_link=videolink)
        return redirect(url_for("home"))
    
    return render_template(APPTHEME.addvideo)




@app.route("/converttoaudio/<book>")
def convert_book_to_audio(book:str):
    from helpers.book_converter import get_booknames

    rd = ReadBook(safe_bookname=book,
                  starting_page=0,
                  base_path_=BASE_PATH,
                  reader_=GLOBALREADER)

    if isinstance(rd.reader,ReaderCoreConnector):
        threading.Thread(target=lambda: rd.async_read_book(socketed_app=socketed_app)).start()
    else:
        threading.Thread(target=lambda: rd.read_book(save=True,socketed_app=socketed_app)).start()

    books = get_booknames(basepath=BASE_PATH)

    return render_template(APPTHEME.convert_book_to_audio,
                           book_id=book,
                           page_count = rd.page_count(),
                           books_name = books.get(book.removesuffix("_readable.json"))
                           )

@app.route("/openorigin/<book>")
def open_book_origin(book):
    """so far this will only ever work with pdfs tracking pages in other formats is rather hard and annoying. Not to mention that i would have to have a way to open them reliably
    without knowing what system apps are installed
    Opens the book to a certain page when reading, this should be helpfull when you want to looks at some diagramm or image, while listening
    """
    if book == None:
        return "No book specified"
    page = request.args.get("page",0)
    from helpers.openorigin import OpenBooksFile
    res = OpenBooksFile(base_path=BASE_PATH,bookname=book,page=page).open_file()
    return jsonify({"success":res})

@app.route("/readbook/<book>")
def read_book_(book:str):
    # load the page of the book, return it as list
    page_data,available = return_cache(book,basepath=BASE_PATH)
    from helpers.book_converter import get_booknames
    books = get_booknames(basepath=BASE_PATH)

    if not available:
        return "book was not converted before"
    current_page = request.args.get("page","0")
    if current_page == "null":
        current_page = 0
    while page_data.get(current_page,"") == "":
        current_page = int(current_page)
        current_page +=1
        current_page = str(current_page)

    return render_template(APPTHEME.read_book,
                           page=page_data[str(current_page)],
                           current_page=current_page,
                           book_id=book.removesuffix("_readable.json"),
                           bookname=book,
                           safe_bookname=books.get(book.removesuffix("_readable.json")))

@app.route("/api/killserver",methods=["POST","GET"])
def kill_server():
    """stops the server from running"""
    if not request.args.get("test"):
        INACTIVITY_MANAGER.interval = 1
        INACTIVITY_MANAGER.auto_shutdown()
        INACTIVITY_MANAGER.set_exit_event()


    if request.method == "GET":
        return render_template(APPTHEME.shutdownscreen)
    else:
        return "kill server called shutting down."

@app.route("/api/alive")
def server_alive():
    """used for checking is the server is up"""
    return jsonify({"alive":True})

@app.route("/api/speak",methods=["POST"])
def speak():
    """speaks, used by the accessibility screen reader function
    can be activated by the r button when any page is in focus
    """
    data = request.get_json(force=True)
    print(data)
    GLOBALREADER.Speak(text=data.get("text","no text passed"))
    return jsonify({"spoken":data.get("text")})

@app.route("/api/makepage/<book>/<page>")
def make_page_of_book(book,page):
    rd = ReadBook(safe_bookname=book,starting_page=page,base_path_=BASE_PATH,reader_=GLOBALREADER)
    rd._on_sentence_progress = None
    blocking = True if request.args.get("blocking",False) == "1" else False
    print("-> make page triggered")
    success = rd.save_page_by_sentences(int(page),blocking=blocking)
    if success == True:
        return jsonify({"page":page,
                        "book":book,
                        "converted":success,
                        "sentence_data":rd.save_transscript_for_page(page)})
    else:
        res = {"success":False}
        if success != False:
            res["error"] = str(success)
        return jsonify(res)


@app.route("/api/show_image/<book>/<page>")
def show_img_from_book(book,page):
    """returns the images from the database if they exists"""
    return "Gone",410
    from helpers.makebrr import PageImageHandler
    img_handler = PageImageHandler(
        base_path=BASE_PATH,
        safe_bookname=book.removesuffix("_readable.json")
    )

    data = img_handler.get_images_of_page(page_number=page)
    return jsonify({
        "success":data
    })


@app.route("/api/pull_notes/<book>/<page>")
def pull_page_notes(book,page):
    notes_handler = NotesHandler(
        base_path=BASE_PATH,
        safe_bookname=book.removesuffix("_readable.json")
    )

    res = notes_handler.get_notes_of_page(page_number=int(page))

    return jsonify({
        "success":res
    })


@app.route("/api/make_note/<book>/<page>",methods=["POST"])
def make_note(book,page):
    notes_handler = NotesHandler(
        base_path=BASE_PATH,
        safe_bookname=book.removesuffix("_readable.json")
    )

    data = request.get_json(force=True)
    note = data["note"]
    sentence_number= data["sentence_number"]

    res = notes_handler.add_note(
        note=note,
        sentence_number=sentence_number,
        page_number=int(page)
    )
    
    return jsonify({
        "success":res
    })


@app.route("/api/del_note/<book>/<note_id>")
def del_note(book,note_id):
    """removes the note from the .brr file"""
    notes_handler = NotesHandler(
        base_path=BASE_PATH,
        safe_bookname=book.removesuffix("_readable.json")
    )

    res = notes_handler.remove_note(note_id=note_id)
    return jsonify({"success":res})

@app.route("/api/update_note/<book>/<note_id>",methods = ["POST"])
def update_note(book,note_id):
    """updated the note to a new value"""
    notes_handler = NotesHandler(
        base_path=BASE_PATH,
        safe_bookname=book.removesuffix("_readable.json")
    )

    data = request.get_json(force=True)


    res = notes_handler.change_note(
        note_id=int(note_id),
        new_note=data.get("note")
    )

    return jsonify({"success":res})





@app.route("/api/pull_cards/<book>/<page_number>")
def pull_cards(book,page_number):
    notes_handler = NotesHandler(
        base_path=BASE_PATH,
        safe_bookname=book
    )

    res = notes_handler.get_notes_of_page(page_number=int(page_number))
    return jsonify({
        "success":res
    })

@app.route("/api/update_card/<book>/card_id")
def update_card(book,card_id):
    card_handler = CardHandler(
        base_path=BASE_PATH,
        safe_bookname=book
    )
    data = request.get_json(force=True)

    front_side_text = data["front_side_text"]
    back_side_text = data["back_side_text"]

    res = card_handler.update_card(
        card_id=int(card_id),
        front_side_text=front_side_text,
        back_side_text=back_side_text
    )

    return jsonify({
        "success":res
    })

@app.route("/api/make_new_card/<book>/<page_number>")
def make_card(book,page_number):

    card_handler = CardHandler(
        base_path=BASE_PATH,
        safe_bookname=book.removesuffix("_readable.json")
    )

    data = request.get_json(force=True)

    front_side_text = data["front_side_text"]
    back_side_text = data["back_side_text"]

    res = card_handler.add_card(
        page_number=page_number,
        front_side_text=front_side_text,
        back_side_text=back_side_text
    )

    return jsonify({
        "success":res
    })


@app.route("/api/delete_card/<book>/<card_id>")
def del_card(book,card_id):
    card_handler = CardHandler(
        base_path=BASE_PATH,
        safe_bookname=book.removesuffix("_readable.json")
    )

    res = card_handler.remove_card(
        card_id=int(card_id)
    )

    return jsonify({
        "success":res
    })


@app.route("/api/testimage",methods = ["POST"])
def test_image_api():
    """checks and retunrs the text extracted from the image"""
    if request.files.get("image"):
        img = request.files.get("image")
        lang = request.form.to_dict()["lang"]
        location = os.path.join(app.config["UPLOAD_FOLDER"],img.filename)
        print(location)
        img.save(dst=location)
        from helpers.book_conversion_from_images import ConvertFromImages
        t = ConvertFromImages.test_one(filename=location,lang=lang)
        return jsonify({"text":t})



@app.route("/api/getpage/<book>")
def return_page_audio(book):
    sentence = request.args.get("sentence")
    if not sentence:
        sentence = 0
    thisissubfolder = os.path.join("books",book.removesuffix("_readable.json"),"tmp",f"sentence_{sentence}.wav")
    print(thisissubfolder)
    return send_file(os.path.join(BASE_PATH,"static",thisissubfolder))


def run_server_just_local():
    thehost = BRRAPPCONFIG["app"]["host"]
    app.run(host=thehost,port=BRRAPPCONFIG["app"]["port"],debug=DEBUG)



@app.before_request
def monitor_inactivity():
    global INACTIVITY_MANAGER
    INACTIVITY_MANAGER.trigger()

def run_server_with_socketio():
    if BRRAPPCONFIG["shutdown"]["auto_shutdown"]:
        #INACTIVITY_MANAGER.max_timeout = int(BRRAPPCONFIG["shutdown"]["shutdown_after"])
        INACTIVITY_MANAGER.auto_shutdown()

    thehost = BRRAPPCONFIG["app"]["host"]
    socketed_app.run(app=app,host=thehost,port=BRRAPPCONFIG["app"]["port"],debug=BRRAPPCONFIG["app"]["debug"],use_reloader=False,allow_unsafe_werkzeug=True)

def run_server_with_reload_trouble_shoot():
    if BRRAPPCONFIG["shutdown"]["auto_shutdown"]:
        #INACTIVITY_MANAGER.max_timeout = int(BRRAPPCONFIG["shutdown"]["shutdown_after"])
        INACTIVITY_MANAGER.auto_shutdown()

    thehost = BRRAPPCONFIG["app"]["host"]
    socketed_app.run(app=app,host=thehost,port=BRRAPPCONFIG["app"]["port"],debug=DEBUG,use_reloader=True,allow_unsafe_werkzeug=False)



if __name__ == "__main__":
    run_server_with_socketio()


    
