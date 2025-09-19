"""converts the images into text, the images need to follow the naming of <page_number>.png or jpeg"""

import os
import shutil
from zipfile import ZipFile
import PIL as pillow
import pytesseract
from secrets import token_urlsafe
import json
from helpers.book_converter import update_booknames
from helpers.thepanic import Pan as pan

class ConvertFromImages():
    """takes a zip file as its argument, the file should be located in the uploads folder"""

    def __init__(self,base_path,zip_filename,book_lang="hun",starting_page=1, ending_page=None):
        self.base_path = base_path
        self.zips_folder = os.path.join(self.base_path,"uploads")
        """contains the uploaded books zip file"""
        self.tmp_folder = os.path.join(self.zips_folder,"tmp")
        """it holds the current books files but deleted the next time its used"""
        self.zip_files_name = zip_filename
        self.book_lang = book_lang
        self._make_missing_folders()
        self.starting_page = starting_page
        self.ending_page = ending_page



    def _make_missing_folders(self):
        """creates the missing folders for the zip book"""
        if not os.path.exists(self.zips_folder):
            os.mkdir(self.zips_folder)

        if not os.path.exists(self.tmp_folder):
            os.mkdir(self.tmp_folder)

    def clean_tmp(self):
        """delete the tmp folder and recreates it after"""
        shutil.rmtree(self.tmp_folder)
        os.mkdir(self.tmp_folder)
        print("cleared tmp of zip")

    @staticmethod
    def test_one(tesseractlocation=r"C:/Program Files/Tesseract-OCR/tesseract.exe",filename="testimage.jpg",lang="eng"):
        """converts one page randomly so we can see what it looks like"""
        pytesseract.pytesseract.tesseract_cmd = tesseractlocation
        from PIL import Image, ImageOps
        img = Image.open(filename)
        img_grayed = ImageOps.grayscale(img)
        text = pytesseract.image_to_string(img_grayed, lang=lang)
        print("After Conversion: ",text)
        return text


    def conversion_fail(self,*args,**kwargs):
        print("try to install pytesseract in your system, this way of reading books is also only supported on desktop not android for now")
        raise kwargs.get("error")
    


    @pan.panic(on_panic="conversion_fail",class_method=True)
    def convert_from_zip(self):
        """if you upload the book in a zip format it will try and convert it, the iamges of the pages need to follow the logic of page_<page_number> -> page_48.png convension"""
        self.clean_tmp()
        with ZipFile(os.path.join(self.zips_folder,self.zip_files_name),"r") as zip_file:
            zip_file.extractall(path=self.tmp_folder)

        page_data = {} 
        pages = os.listdir(self.tmp_folder)

        pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
        for i ,page in enumerate(pages):
            print(f"processing image {i}")
            from PIL import Image,ImageOps
            img = Image.open(os.path.join(self.tmp_folder,page))
            img_gray = ImageOps.grayscale(img) 
            text = pytesseract.image_to_string(img_gray, lang=self.book_lang)
            page_data[str(i)] = text

        safe_name = token_urlsafe(32)
        books_json_path =os.path.join(self.base_path,"static","books",f"{safe_name}_readable.json") 
        print(books_json_path)

        with open(books_json_path,"w") as converted:
            json.dump(page_data,converted,indent=4)

        update_booknames(safe_name,self.zip_files_name.removesuffix(".zip"),basepath=self.base_path)
        return page_data,f"{safe_name}_readable.json"



