from flask import Flask
from flask import request,redirect,url_for,render_template,jsonify,send_file
from werkzeug.utils import secure_filename


import os
import sys
import threading

# this block is for pyinstaller to pick up the files correctly
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
# -- -- -- -- -- -- -- 

from helpers.book_converter import return_cache,get_booknames,make_permanent_by_page
from helpers.generalttsreader import ReadBook
from helpers.loadreader import load_reader, get_readers_config
from plusreaders import readers as custom_readers
from helpers.bookreaders import readers as builtin_readers
from helpers.store import VoiceStorePiper


import flask_socketio
from flask_socketio import SocketIO
import socketio




try:
    from android.storage import app_storage_path
    BASE_PATH = os.path.join(app_storage_path(),"app")
    DEBUG = False
    ONANDROID = True
except:
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        BASE_PATH = sys._MEIPASS
        print(BASE_PATH)
        DEBUG = False
        ONANDROID = False

    else:
        # Running as normal Python script
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        print(BASE_PATH)
        DEBUG = True
        ONANDROID = False


    #print(os.listdir(BASE_PATH))


SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
GLOBALREADER = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)



def re_initialize_reader():
    """sets a new global reader if there is a settings change"""
    global SELECTED_READER,READERS_CONFIG,GLOBALREADER
    SELECTED_READER = load_reader(base_path=BASE_PATH,custom_readers=custom_readers,builtin_readers=builtin_readers)
    READERS_CONFIG = get_readers_config(base_path=BASE_PATH,readername=SELECTED_READER.__name__)
    GLOBALREADER = SELECTED_READER(**READERS_CONFIG,base_path = BASE_PATH)




print("this is basepath:",BASE_PATH)
app = Flask(__name__,template_folder=os.path.join(BASE_PATH,"templates"),static_folder=os.path.join(BASE_PATH,"static"))
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_PATH,"uploads")
socketed_app = SocketIO(app=app,async_mode="threading")

@app.route("/")
def home():
    books = get_booknames(basepath=BASE_PATH)
    return render_template("index.html",books=books)


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
    if request.method == "POST":
        # we check image quality here
        if request.files.get("image"):
            img = request.files.get("image")
            location = os.path.join(app.config["UPLOAD_FOLDER"],img.filename)
            print(location)
            img.save(dst=location)
            from helpers.book_conversion_from_images import ConvertFromImages
            t = ConvertFromImages.test_one(filename=location,lang="hun")
            return t
    return render_template("testimage.html")



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


@app.route("/<book>")
def read_book_(book):
    # load the page of the book, return it as list
    page_data,available = return_cache(book,basepath=BASE_PATH)
    if not available:
        return "book was not converted before"
    current_page = request.args.get("page","0")
    while page_data.get(current_page,"") == "":
        current_page = int(current_page)
        current_page +=1
        current_page = str(current_page)

    return render_template("readpage.html",page=page_data[str(current_page)],current_page=current_page,bookname=book,readable_name=get_booknames(basepath=BASE_PATH).get(book.removesuffix("_readable.json")))



@app.route("/api/makepage/<book>/<page>")
def make_page_of_book(book,page):
    rd = ReadBook(safe_bookname=book,starting_page=page,base_path_=BASE_PATH,reader_=GLOBALREADER)
    rd._on_sentence_progress = None
    success = rd.save_page_by_sentences(page)
    print("-> make page triggered")
    return jsonify({"page":page,"book":book,"converted":success,"sentence_data":rd.save_transscript_for_page(page)})

@app.route("/api/yieldpagetext/<book>/<page>")
def yieldbooktext(book,page):
    """returns the nltk converted sentences so we can use the browsers text to speech to listen to the book"""
    data,success = return_cache(book)
    if success:
        return jsonify(nltk.sent_tokenize(data[str(page)]))
    else:
        return "some error happened, make sure the books name is typed correctly"


@app.route("/api/getpage/<book>")
def return_page_audio(book):
    sentence = request.args.get("sentence") 
    if not sentence:
        sentence = 0
    thisissubfolder = os.path.join("books",book.removesuffix("_readable.json"),"tmp",f"sentence_{sentence}.wav")
    print(thisissubfolder)
    return send_file(os.path.join(BASE_PATH,"static",thisissubfolder))


def run_server_just_local():
    app.run(host="localhost",port=5003,debug=DEBUG)



def run_server_with_socketio():
    thehost = "localhost" if not DEBUG else "0.0.0.0"
    socketed_app.run(app=app,host=thehost,port=5003,debug=DEBUG)

if __name__ == "__main__":
    #run_server_just_local()
    run_server_with_socketio()

