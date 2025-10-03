import webbrowser
import os
from urllib.parse import urljoin


class OpenBooksFile():

    def __init__(self,base_path,bookname,page):
        self.bookname = bookname
        self.page = page
        self.basepath = base_path
        self.uploads_folder = os.path.join(self.basepath,"uploads")
        "PATH"
    def check_type(self):
        """ we only ever want to open pdf files nothing else"""
        ending = self.bookname.rsplit(".")[-1]
        print("ending:",ending)
        match ending:
            case "pdf":
                return True            
            case _:
                return False
                #raise BaseException("other endings are not supported currently")


    def open_file(self):
        if self.check_type():
            theurl = f"http://localhost:5003/uploads/{self.bookname}#page={self.page}"
            #filepath = "file:///" + os.path.join(self.uploads_folder, self.bookname).replace("\\", "/") + f"#page={self.page}"
            webbrowser.open(theurl)
        else:
            print("this method is only gonna work with pdfs")
if __name__ == "__main__":
    openpdf = OpenBooksFile(
        base_path=r"c:/Users/ishall/Desktop/public_brainrootreader/brainrootreader",
        bookname="README.pdf",
        page=2
    )
    openpdf.open_file()