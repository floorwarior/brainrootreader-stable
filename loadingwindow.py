import tkinter
from tkinter import Tk,Frame,Label
import os
import webbrowser
import time
import sys
import signal
import threading

# ---------------------------
from __version__ import __version__ , __released__
from helpers.pingserver import kill_server,is_server,health_check
from helpers.settings import load_app_config 
from helpers.stringloader import SimpleStringLoader
from helpers.thepanic import Pan as pan
# ---------------------------

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    ISFROZEN = True
    BASE_PATH = sys._MEIPASS
    print(BASE_PATH)

else:
    # Running as normal Python script
    ISFROZEN = False
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))
    print(BASE_PATH)
    DEBUG = False

BRRAPPCONFIG = load_app_config(basepath=BASE_PATH)


def run_splash_screen():
    tkapp = Tk()
    style = {
        "header":("Sans",26,"bold"),
        "bottom_texts":("Sans",16),
        "theme_color":"#181818",
        "text_color":"#FFFFFF"
    }


    topbar = Frame(master=tkapp,bd=1,relief="flat",bg="#181818")
    middle = Frame(master=tkapp,bd=1,relief="flat",bg="#181818")
    bottom = Frame(master=tkapp,bd=1,relief="flat",padx=20,bg="#181818")


    topbar.pack(side="top",fill="x")
    middle.pack(fill="both",expand=True)
    bottom.pack(side="bottom",fill="x")


    header = Label(master=topbar,text="Brain Root Reader",font=style["header"],fg=style["text_color"],bg=style["theme_color"])
    version_number = Label(bottom,text=f"version: {__version__}",font=style["bottom_texts"],fg=style["text_color"],bg=style["theme_color"])
    maker = Label(bottom,text="by floorwarior",font=style["bottom_texts"],fg=style["text_color"],bg=style["theme_color"])
    dated = Label(bottom,text=f"{__released__}",font=style["bottom_texts"],fg=style["text_color"],bg=style["theme_color"])

    loading_label = Label(middle,text="Loading",font=style["bottom_texts"],fg=style["text_color"],bg=style["theme_color"])

    header.pack()
    version_number.pack(side="right")
    maker.pack(side="left")
    dated.pack()
    loading_label.pack()

    #tkapp.overrideredirect(True)
    tkapp.title("Brain Root Reader")
    tkapp.iconbitmap(os.path.join(BASE_PATH,"brainrootreadericon.ico"))
    screen_width = tkapp.winfo_screenwidth()
    screen_height = tkapp.winfo_screenheight()
    height = 400
    width = 750

    x = (screen_width - width) // 2 
    y = (screen_height - height) // 2

    def close():
        kill_server()
        tkapp.destroy()


    def auto_stop():
        def helper():
            while health_check():
                time.sleep(30)
            pid = os.getpid()
            os.kill(pid,signal.SIGINT)

        th = threading.Thread(target=helper)
        th.start()

    loadingbar = SimpleStringLoader(label=loading_label)
    loadingbar.start()

    def open_browser():
        """once the server is open we want to redirect the user to it"""
        nonlocal loadingbar
        def helper():
            if is_server():
                webbrowser.open("http://localhost:5003",new=1)
                if BRRAPPCONFIG.get("auto_shutdown"):
                    tkapp.destroy()
                else:
                    tkapp.protocol("WM_DELETE_WINDOW", close)
            else:
                pan.logger.error(msg="Server is unavailable, loading window exiting.")
                tkapp.destroy()

            loadingbar.stop()
            tkapp.after(4000,lambda : loading_label.config(text=" "))


        th = threading.Thread(target=helper,daemon=True)
        th.start()





    tkapp.geometry(f"{width}x{height}+{x}+{y}")
    tkapp.after(750,open_browser)
    tkapp.after(60000,auto_stop) # stops the window if the server becomes unavailable

    tkapp.mainloop()

if __name__ == "__main__":
    run_splash_screen()