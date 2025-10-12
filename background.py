import subprocess
import multiprocessing
import os
import threading
import sys


#window_process = multiprocessing.Process(target=window_stuff)

#print(CURRENT_PYTHON)




if getattr(sys, 'frozen', False):
    # Running as compiled executable
    ISFROZEN = True
    BASE_PATH = sys._MEIPASS
    print(BASE_PATH)
    DEBUG = False
    ONANDROID = False
    CURRENT_PYTHON = "python.exe"

else:
    # Running as normal Python script
    ISFROZEN = False
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    print(BASE_PATH)
    DEBUG = False
    ONANDROID = False
    CURRENT_PYTHON = sys.executable


subprocess.Popen([CURRENT_PYTHON,os.path.join(BASE_PATH,"loadingwindow.py") ,"--basepath",BASE_PATH])


from flask import Flask
from flask import request,redirect,url_for,render_template,jsonify,send_file
from werkzeug.utils import secure_filename
from flask import send_from_directory


# this block is for pyinstaller to pick up the files correctly, you can comment this out if you are not building only using the app
import helpers
import engineio
import plusreaders 
import readerconfigs
import pypdf
import piper
import pythoncom
import nltk
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

#from TTS.api import TTS
# -- -- -- -- -- -- -- 

from helpers.book_converter import return_cache,get_booknames,make_permanent_by_page
from helpers.generalttsreader import ReadBook
from helpers.loadreader import load_reader, get_readers_config
from plusreaders import readers as custom_readers
from helpers.bookreaders import readers as builtin_readers
from helpers.store import VoiceStorePiper
from helpers.readercore_connector import ReaderCoreConnector

from flask_socketio import SocketIO

#SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
#READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
 
#GLOBALREADER = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)
# if you have a better you should use this new method called ReaderCoreConnector
# it makes it possible to run more then one instances of the reader classes as it wraps them
# i tested it with i-5 7500 and after a coldstart it can run kokoro, you will need to wait for the first 3 pages to generate however, or if you are jumping around
GLOBALREADER  = ReaderCoreConnector(
    core_count = 2,
    is_frozen = ISFROZEN
)


def re_initialize_reader():
    """sets a new global reader if there is a settings change"""
    global GLOBALREADER
    #SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
    #READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
    GLOBALREADER = ReaderCoreConnector(
        core_count = 3,
        is_frozen = ISFROZEN
    )




print("this is basepath:",BASE_PATH)
app = Flask(__name__,template_folder=os.path.join(BASE_PATH,"templates"),static_folder=os.path.join(BASE_PATH,"static"))
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_PATH,"uploads")
socketed_app = SocketIO(app=app,async_mode="threading")

@app.route("/")
def home():
    books = get_booknames(basepath=BASE_PATH)
    return render_template("index_v2.html",books=books)


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
    stores = {piper_voice_store.name:piper_voice_store}
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
    return render_template("voicebag.html",voicestores=[piper_voice_store])

@app.route("/settings",methods=["POST","GET"])
def settings():
    #return "<h1>This does not work</h1>"
    if request.method == "POST":
        from helpers.settings import save_settings
        data = request.form.to_dict()
        save_settings(base_path=BASE_PATH,data=data)
        re_initialize_reader()
        return redirect(url_for("home"))
    else:
        from helpers.loadreader import all_readers
        from helpers.videos import get_video_list
        # Gets all the voices from all readers except of the browser one that is handled in the browser
        return render_template("settings.html",all_readers = all_readers(custom_readers,builtin_readers),get_readers_config=get_readers_config,base_path=BASE_PATH,videos=get_video_list(BASE_PATH),selected_reader=SELECTED_READER)

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
    from helpers.book_converter import get_booknames        
    return render_template("testimage_v2.html",books=get_booknames(basepath=BASE_PATH))


@app.route("/testnewroutes")
def check_new_routes():
    """testing the new route layouts here"""
    from helpers.book_converter import get_booknames
    books = get_booknames(basepath=BASE_PATH)
    return render_template("testimage_v2.html",books=books)


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



@app.route("/addvideo",methods=["POST","GET"])
def add_video():
    """allows the user to add any video to be played by the app
    """
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
    
    return render_template("uploadvideo.html")



@app.route("/converttoaudio/<book>")
def convert_book_to_audio(book):
    global ONANDROID
    rd = ReadBook(safe_bookname=book,
                  starting_page=0,
                  base_path_=BASE_PATH,
                  reader_=GLOBALREADER)
    rd._on_sentence_progress = None
    rd._on_page_progress = lambda *args,**kwargs : socketed_app.emit(event="progress",data={"book_id":book,"page_num":kwargs.get("page_num"),"page":kwargs.get("page")})
    def onfinished_callback(*args,**kwargs):
        socketed_app.emit(event="finished",data={"book_id":book,"book_folder":kwargs.get("book_folder")})
        os.startfile(kwargs.get("book_folder"))
    rd._on_conversion_finished = lambda *args, **kwargs :onfinished_callback(*args,**kwargs)
    th = threading.Thread(target=lambda: rd.read_book(save=True))
    th.start()
    return render_template("convertingbooktoplaylist.html",book_id=book,page_count = rd.page_count())


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
def read_book_(book):
    # load the page of the book, return it as list
    page_data,available = return_cache(book,basepath=BASE_PATH)
    from helpers.book_converter import get_booknames
    books = get_booknames(basepath=BASE_PATH)

    if not available:
        return "book was not converted before"
    current_page = request.args.get("page","0")
    while page_data.get(current_page,"") == "":
        current_page = int(current_page)
        current_page +=1
        current_page = str(current_page)

    return render_template("readpage_v2.html",page=page_data[str(current_page)],current_page=current_page,bookname=book,readable_name=books.get(book.removesuffix("_readable.json")),books=books)

@app.route("/api/killserver")
def kill_server():
    """stops the server from running"""
    import signal
    import time
    pid = os.getpid()
    def shutdown():
        print("kill server called shutting down.")
        time.sleep(2)
        GLOBALREADER.clean_up()
        os.kill(pid,signal.SIGINT)
    threading.Thread(target=shutdown).start()
    return jsonify({"request":"shutdown server","status":"scheduled","Brain Root Reader":"bye bye see you next time"})


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
    success = rd.save_page_by_sentences(page)
    print("-> make page triggered")
    return jsonify({"page":page,"book":book,"converted":success,"sentence_data":rd.save_transscript_for_page(page)})



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
    thehost = "localhost" if not DEBUG else "0.0.0.0"
    app.run(host=thehost,port=5003,debug=DEBUG)

def run_server_with_socketio():
    thehost = "localhost" if not DEBUG else "0.0.0.0"
    socketed_app.run(app=app,host=thehost,port=5003,debug=DEBUG,use_reloader=False)




if __name__ == "__main__":
    run_server_with_socketio()