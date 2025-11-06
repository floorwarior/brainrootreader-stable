"""what is .brr? 
brr is a compact form which allows you to transport your documents in one singular file,
it stores your comments, flashcards relevant to each page
it also has the images of the original document
"""
try:
    from helpers.databaselogic import dbModel
except:
    from databaselogic import dbModel

import os
from typing import Literal
import base64


class NotesHandler():


    def __init__(self,*args,base_path,safe_bookname,**kwargs):
        self.base_path = base_path
        self.books_folder = os.path.join(self.base_path,"static","books")
        self.safe_bookname = safe_bookname
        self.db_name = f"brr_{self.safe_bookname}.brr"
        self.table_name = "notes"

        self.db = dbModel(
            db_name=os.path.join(self.books_folder,self.db_name),     
            db_folder=self.books_folder,
            table_name=self.table_name,
            col_names=["note_id","page_number","note","sentence_number"],
            col_type=["INTEGER PRIMARY KEY AUTOINCREMENT",
                      "INTEGER",
                      "TEXT",
                      "INTEGER"],
                          )
        
    def remove_note(self,note_id):
        self.db.delete(conditions=["note_id = ?"],values=[note_id])

    def add_note(self,note,page_number,sentence_number):
        """
        - note: 'remember that this will be in the exam'
        - sentence_number: 10
        - page_number: 45
        """
        return self.db.create_new_entry({"note":note,"page_number":page_number,"sentence_number":sentence_number,},strict=False)

    def change_note(self,note_id,new_note):
        self.db.update(col_name="note_id",col_val=note_id,what=["note"],to=[new_note])


    def _order_notes(self,data):
        ordered = {}
        for d in data:
            if not d["sentence_number"] in ordered.keys():
                sentence_number = d["sentence_number"]
                ordered[sentence_number] = [d]
            else:
                ordered[sentence_number].append(d)

        return ordered

    def get_notes_of_page(self,page_number):
        """returns all the notes placed on a specific page"""
        data = self.db.find_where(
            col_name=["page_number","note","sentence_number","note_id"],
            getall=True,
            conditions=["page_number = ?"],values=[page_number]
        )
        return self._order_notes(data)


class CardHandler():

    def __init__(self,base_path,safe_bookname):
        self.base_path = base_path
        self.books_folder = os.path.join(self.base_path,"static","books")
        self.safe_bookname = safe_bookname
        self.db_name = f"brr_{self.safe_bookname}.brr"
        self.table_name = "cards"

        self.db = dbModel(
            db_name=os.path.join(self.books_folder,self.db_name),     
            db_folder=self.books_folder,
            table_name=self.table_name,
            col_names=["card_id","front_side_text","back_side_text","page_number"],
            col_type=["INTEGER PRIMARY KEY AUTOINCREMENT",
                      "TEXT",
                      "TEXT",
                      "INTEGER"],
                          )

    def add_card(self,front_side_text,back_side_text,page_number):
        """
        - front_side_text: What powers the cell?
        - back_side_text: The mithocondria is the powerhouse of the cell.
        - card_id: 10
        - page_number: 45
        """
        self.db.create_new_entry({"front_side_text":front_side_text,"back_side_text":back_side_text,"page_number":page_number},strict=False)
        
    def remove_card(self,card_id):
        self.db.delete(conditions=["card_id = ?"],values=[card_id])

    def update_card(self,card_id,front_side_text,back_side_text):
        self.db.update(col_name="card_id",col_val=card_id,what=["front_side_text","back_side_text"],to=[front_side_text,back_side_text])



    def get_cards_of_page(self,page_number):
        """returns all the notes placed on a specific page"""
        data = self.db.find_where(
            col_name=["page_number","front_side_text","back_side_text","card_id"],
            getall=True,
            conditions=["page_number = ?"],values=[page_number]
        )
        return data


class PageTextHandler():
    def __init__(self,base_path,safe_bookname):
        self.base_path = base_path
        self.books_folder = os.path.join(self.base_path,"static","books")
        self.safe_bookname = safe_bookname
        self.db_name = f"brr_{self.safe_bookname}.brr"
        self.table_name = "pages"

        self.db = dbModel(
            db_name=os.path.join(self.books_folder,self.db_name),     
            db_folder=self.books_folder,
            table_name=self.table_name,
            col_names=["page_id","page_text","page_number"],
            col_type=["INTEGER PRIMARY KEY AUTOINCREMENT",
                      "TEXT",
                      "INTEGER"
                      ])
        

    def insert_all(self,datadict):
        values = []
        placeholders = []

        for key,val in datadict.items():
            values.append(key)
            values.append(val)

            placeholders.append(f"( ? , ? )")

        placeholder = ",".join(placeholders)

        self.db.exec_any(
            command=f"""
        INSERT
            INTO {self.db.table_name}
                ( page_number , page_text )
            VALUES
                {placeholder}
""",values=values,confirm=False
        )


    def get_text_of_page(self,page_number):
        """retuns the text of a page"""

        return self.db.find_where(
            col_name=["page_text","page_number","page_id"],conditions=["page_number = ?"],values=[page_number],getall=False
        )



class PageImageHandler():


    def __init__(self,base_path,safe_bookname):
        self.base_path = base_path
        self.books_folder = os.path.join(self.base_path,"static","books")
        self.safe_bookname = safe_bookname
        self.db_name = f"brr_{self.safe_bookname}.brr"
        self.table_name = "images"

        self.db = dbModel(
            db_name=os.path.join(self.books_folder,self.db_name),     
            db_folder=self.books_folder,
            table_name=self.table_name,
            col_names=["image_id","page_number","img_data"],
            col_type=["INTEGER PRIMARY KEY AUTOINCREMENT",
                      "INTEGER",
                      "BLOB",
                      ])


    def convert_image(self,img):
        """turns image into byte strings"""
        encoded1 = None
        
        if img:
            # Read file bytes and convert to base64
            encoded1 = base64.b64encode(img).decode('utf-8')

        if encoded1:
            return f"data:image/*;base64,{encoded1}"
        else:
            return False



    def insert_imgs_by_page(self,page_number,imgs):
        """inserts all the images into the database, takes a dictionary that contains the images of the book and on what page was it found
        """
        values = []
        placeholders = []


        if not imgs:
            return

        for img in imgs:
            values.append(page_number)
            if (x:=self.convert_image(img.data)):
                values.append(x)
            placeholders.append(f"( ? , ? )")

        placeholder = ",".join(placeholders)

        self.db.exec_any(
            command=f"""
        INSERT
            INTO {self.db.table_name}
                ( page_number , img_data )
            VALUES
                {placeholder}
    """,values=values,confirm=False
        )


    def get_images_of_page(self,page_number):
        """returns the images from a certain page"""

        data : list = self.db.find_where(
            col_name=["image_id","page_number","img_data"],
            conditions=["page_number = ?"],values=[page_number]
        )
        return data


class RemoveBrrFile():

    def __init__(self,base_path,safe_bookname):
        self.base_path = base_path
        self.books_folder = os.path.join(self.base_path,"static","books")
        self.safe_bookname = safe_bookname
        self.db_name = f"brr_{self.safe_bookname}.brr"


    def remove_brr(self):
        db_path = os.path.join(self.base_path,"static","books",self.db_name)
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    # brr_GuI6C2pGbdGOSBhDgIFDPuHmP8KsUL3I92zCPTeYuDU.brr
    text_handler = PageTextHandler(base_path=r"c:\Users\ishall\Desktop\public_brainrootreader\brainrootreader",safe_bookname="larrybird")
    text_handler.db.get_db_state()
    
