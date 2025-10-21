import docx
import os
from secrets import token_urlsafe
import json
from helpers.book_converter import update_booknames
from helpers.thepanic import Pan as pan

class ConvertFromDocx():

    def __init__(self,basepath,docx_name,chunksize = 15):
        self.base_path= basepath
        self.docx_name = docx_name
        "NOT A PATH just a filename"
        self.upload_folder = os.path.join(self.base_path,"uploads")
        "PATH"
        from nltk import sent_tokenize
        self.sent_tokenize = sent_tokenize
        self.chunksize = chunksize
        self._convert_error_handler = lambda *args, **kwargs: print("the conversion of the file failed with error,",kwargs.get("error"), "look at the above traceback to see where it went wrong")

    def _chunkit(self,text):
        """breaks the submitted text into 15 sentence pages"""
        sentences = self.sent_tokenize(text)
        current_page = 0
        pages = {}
        for i in range(0,len(sentences),self.chunksize):
            pages[current_page] = " ".join(sentences[i:i+self.chunksize])
            current_page += 1

        return pages


    def _gettext(self):
        doc = docx.Document(os.path.join(self.upload_folder,self.docx_name))
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return ' '.join(fullText)


    def convert_error_handler(self,*args,**kwargs):
        if self._convert_error_handler:
            self._convert_error_handler(*args,**kwargs)


    @pan.panic(on_panic="convert_error_handler",class_method=True)
    def convert_from_docx(self):
        """retuns the converted pages, and the safename of the docoument"""
        print("convert docx is running")
       
        text = self._gettext()
        pages = self._chunkit(text)



        safe_name = token_urlsafe(32)
        books_json_path =os.path.join(self.base_path,"static","books",f"{safe_name}_readable.json") 
        print(books_json_path)

        with open(books_json_path,"w") as converted:
            json.dump(pages,converted,indent=4)

        update_booknames(safe_name,self.docx_name,basepath=self.base_path)
        return pages,f"{safe_name}_readable.json"



