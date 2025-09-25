import os
from secrets import token_urlsafe
import json
from helpers.book_converter import update_booknames
from helpers.thepanic import Pan as pan

class ConvertFromTxt():

    def __init__(self,basepath,txtfilename,chunksize=15):
        self.base_path= basepath
        self.txtfilename = txtfilename
        "NOT A PATH just a filename"
        self.upload_folder = os.path.join(self.base_path,"uploads")
        "PATH"
        self.chunksize=chunksize
        "THIS is How many sentences a page will contain not perfect but better then nothing"
        from nltk import sent_tokenize
        self.sent_tokenize = sent_tokenize



    def conversion_fail(self,*args,**kwargs):
        """if the conversion fails we call this function"""
        print("page conversion from file:",)
        print(kwargs.get("error"))



    @pan.panic(on_panic="")
    def convert_txt_file(self):
        """chunks up the text file into into 15 sentence a page chuks"""
        with open(os.path.join(self.upload_folder,self.txtfilename),"r") as txt_file:
            data =  txt_file.readlines()
            cleaned_data = [i.removesuffix("\n") for i in data]

        full_file = " ".join(cleaned_data)
        sentences = self.sent_tokenize(full_file)
        pages ={}
        current_page = 0
        for i in range(0,len(sentences)-1,self.chunksize):
            pages[current_page] = " ".join(sentences[i:i+self.chunksize])
            current_page += 1

        safe_name = token_urlsafe(32)
        books_json_path =os.path.join(self.base_path,"static","books",f"{safe_name}_readable.json") 
        print(books_json_path)

        with open(books_json_path,"w") as converted:
            json.dump(pages,converted,indent=4)

        update_booknames(safe_name,self.txtfilename,basepath=self.base_path)
        return pages,f"{safe_name}_readable.json"

