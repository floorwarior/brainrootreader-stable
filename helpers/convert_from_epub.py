import os
import shutil
from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT
from nltk import sent_tokenize
from secrets import token_urlsafe
import json
from helpers.book_converter import update_booknames



class ConvertFromEbook():

    def __init__(self,basepath,ebookname,chunksize=15):
        self.base_path= basepath
        self.ebookname = ebookname
        "NOT A PATH just a filename"
        self.upload_folder = os.path.join(self.base_path,"uploads")
        "PATH"
        self.epubs_folder = os.path.join(self.upload_folder,"epubs")
        "PATH"
        self.tmp_folder = os.path.join(self.epubs_folder,"tmp")
        "PATH"
        self.chunksize=chunksize
        "THIS is How many sentences a page will contain not perfect but better then nothing"


        self._make_missing_folders()

    def _chunker(self,current_page,chapter):
        """chunks up the item into page size parts"""
        sentences = sent_tokenize(chapter)
        data = {}
        for i in range(0,len(sentences),self.chunksize):
            chunk = sentences[i:i+self.chunksize]
            if chunk:
                data[current_page] = " ".join(chunk)
                current_page += 1


        return current_page, data



    def _make_missing_folders(self):
        if not os.path.exists(self.epubs_folder):
            os.mkdir(self.epubs_folder)

        if not os.path.exists(self.tmp_folder):
            os.mkdir(self.tmp_folder)


    def clear_tmp_folder(self):
        """removes the temp folder and all of its contents"""
        shutil.rmtree(os.path.join(self.tmp_folder))
        os.mkdir(self.tmp_folder)

    def convert_ebook(self):
        self.clear_tmp_folder()
        print("convert ebook is running")
        chapters = epub.read_epub(os.path.join(self.upload_folder,self.ebookname))
        page = 0
        book_data = {}
        for item in chapters.get_items_of_type(ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            #print("this is page:", soup.get_text().strip())
            page, data = self._chunker(page,soup.get_text().strip())
            print("this is page data: ",data)
            book_data.update(data)

        safe_name = token_urlsafe(32)
        books_json_path =os.path.join(self.base_path,"static","books",f"{safe_name}_readable.json") 
        print(books_json_path)

        with open(books_json_path,"w") as converted:
            json.dump(book_data,converted,indent=4)

        update_booknames(safe_name,self.ebookname,basepath=self.base_path)
        return book_data,f"{safe_name}_readable.json"





