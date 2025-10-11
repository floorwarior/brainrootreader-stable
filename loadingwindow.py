import tkinter
from tkinter import Tk,Frame,Label
from helpers.pingserver import kill_server,is_server
import webbrowser

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
    version_number = Label(bottom,text="version: 3.2.0.7",font=style["bottom_texts"],fg=style["text_color"],bg=style["theme_color"])
    maker = Label(bottom,text="by floorwarior",font=style["bottom_texts"],fg=style["text_color"],bg=style["theme_color"])
    dated = Label(bottom,text="2025.10.10",font=style["bottom_texts"],fg=style["text_color"],bg=style["theme_color"])

    header.pack()
    version_number.pack(side="right")
    maker.pack(side="left")
    dated.pack()


    tkapp.overrideredirect(True)
    tkapp.title("Brain Root Reader")
    tkapp.iconbitmap("brainrootreadericon.ico")
    screen_width = tkapp.winfo_screenwidth()
    screen_height = tkapp.winfo_screenheight()
    height = 400
    width = 750

    x = (screen_width - width) // 2 
    y = (screen_height - height) // 2

    def open_browser():
        """once the server is open we want to redirect the user to it"""
        if is_server():
            webbrowser.open("http://localhost:5003")
            tkapp.destroy()


    tkapp.geometry(f"{width}x{height}+{x}+{y}")
    tkapp.after(750,open_browser)
    tkapp.mainloop()

if __name__ == "__main__":
    run_splash_screen()