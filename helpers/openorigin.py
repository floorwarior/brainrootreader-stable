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
        ending = self.bookname.rsplit()[-1]
        match ending:
            case "pdf":
                return True            
            case _:
                return False
                #raise BaseException("other endings are not supported currently")


    def open_file(self):
        filepath = "file:///" + os.path.join(self.uploads_folder, self.bookname).replace("\\", "/") + f"#page={self.page}"
        print("attempting to open:",filepath)
        webbrowser.open(filepath, page=self.page)
        # NOTE: This does not appear to open to book to the correct page unfortunatly, if you have an idea or code to fix this make a pull request

if __name__ == "__main__":
    openpdf = OpenBooksFile(
        base_path=r"c:/Users/ishall/Desktop/public_brainrootreader/brainrootreader",
        bookname="README.pdf",
        page=2
    )
    openpdf.open_file()