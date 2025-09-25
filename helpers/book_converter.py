import os
from pypdf import PdfReader
import json
from secrets import token_urlsafe


def update_booknames(url_safe_name,bookname,basepath=None):
    """adds the new book to the list"""
    if not basepath:
        raise BaseException("no basepath provided for update bookname")
    previous = get_booknames(basepath=basepath)
    previous[url_safe_name] = bookname
    with open(os.path.join(basepath,"booklist.json"),"w") as readytoupdate:
        json.dump(previous,readytoupdate,indent=4)


def get_booknames(basepath=None):
    """returns the current booklist"""
    if not basepath:
        raise BaseException("get booknames recived no basepath")
    temp = []

    with open(os.path.join(basepath,"booklist.json"),"r") as converted_books:
        temp = json.load(converted_books)
    
    return temp



class ConvertFromPdf():

    def __init__(self,base_path,pdf_name):
        self.base_path  :str=  base_path
        "PATH"
        self.upload_folder :str= os.path.join(self.base_path,"uploads")
        "PATH"
        self.static_folder : str = os.path.join(self.base_path,"static")
        "PATH"
        self.books_folder :str = os.path.join(self.static_folder,"books") # this is the folder where all the books are
        "PATH of the books folder NOT this book's folder"
        self.pdf_name :str = pdf_name
        "NOT A PATH only a filename"


    def convert_book(self):
        """convert the pdf into the json file"""
        safe_name = token_urlsafe(32)

        pdf_path = os.path.join(self.upload_folder,self.pdf_name)
        book_data = PdfReader(pdf_path)
        temp = {}
        static_folder = "static"
        books_folder = "books"


        stripped_name = self.pdf_name
        for i,page in enumerate(book_data.pages):
            text = page.extract_text()
            if text != "":
                temp[i] = text
        books_json_path =os.path.join(self.base_path,static_folder,books_folder,f"{safe_name}_readable.json") 
        print(books_json_path)

        with open(books_json_path,"w") as converted:
            json.dump(temp,converted,indent=4)

        update_booknames(safe_name,stripped_name,basepath=self.base_path)
        return temp,f"{safe_name}_readable.json"




def make_permanent_by_page(*args,book:str,basename=None,**kwargs):
    """
    Converts the book form zip, pdf or epub into a json file that has the pages text as key value pairs
    This is the one that is later used for reading so we do not have to covert the images more times
    """
    if not basename:
        raise BaseException("no basename provided for make_permanent_by_page")
    
    accepted_endings = ["zip","pdf","epub"]
    ending = book.rsplit(".")[-1]
    print(ending)

    match ending:
        case "pdf":
            res = ConvertFromPdf(
                base_path=basename,pdf_name=book
            ).convert_book()
        case "epub":
            from helpers.convert_from_epub import ConvertFromEbook
            res = ConvertFromEbook(
                basepath=basename,
                ebookname=book,
            ).convert_ebook()
        case "zip":
            from helpers.book_conversion_from_images import ConvertFromImages
            res = ConvertFromImages(
                base_path=basename,
                zip_filename=book,
                book_lang=kwargs.get("lang","hun")
            ).convert_from_zip()
        case "txt":
            from helpers.book_conversion_from_txt import ConvertFromTxt
            res = ConvertFromTxt(
                basepath=basename,
                txtfilename=book,
            ).convert_txt_file()
        case _:
            raise BaseException(f"book {book} does not have one of the accepted ending: {accepted_endings}")
    return res

def return_cache(safe_bookname,basepath):
    """
    #### gets the book that has already has been converted

    **Returns**
    - data : dict -> contains the books pages with the keys as string
    - success : bool -> if it was converted before    
    """
    if not basepath or not safe_bookname:
        raise BaseException(f"no basepath or safe bookname provided for return cache; basename:{basepath}, safe_name:{safe_bookname}")
    foldername = "static"
    books_folder = "books"
    data = None
    success = False
    thepath = os.path.join(basepath,foldername,books_folder,safe_bookname)
    print(thepath)
    if os.path.exists(thepath):
        with open(os.path.join(basepath,foldername,books_folder,safe_bookname),"r") as already_converted:
            data = json.load(already_converted)
        success = True
    return data, success

