"""what is .brr? 
brr is a compact form which allows you to transport your books in one singular file,
it stores your comments flashcards relevant to each page
it also has the images of the original book
"""
from helpers.databaselogic import dbModel
import os
from typing import Literal

class BrrHandler():
    """makes an empty brr file for your book"""

    def __init__(self,base_path,safe_bookname):
        self.basepath = base_path
        """is a PATH"""
        self.safe_bookname= safe_bookname
        self.db_folder = os.path.join(self.basepath,"static","books")
        """is a PATH"""
        self.tables  = {}

    def get(self,table : Literal["notes","pages","setences","images"] ,search_dict :dict={"page_number":"45","sentence_number":"12"}):
        """ 
            search dict: key -> col of the database, value -> this is the items that the search will look for
            table: name of the table we search from 
        """
        current_table :dbModel = self.tables.get(table)
        values = search_dict.value()
        conditions = [f"{key} = ?" for key in search_dict.keys()]
        current_table.find_where(col_name=["values"],conditions=conditions,values=values)



    def put(self,table  : Literal["notes","pages","setences","images"],):
        current_table :dbModel = self.tables.get(table)
        current_table.multi_update()

        


    def create_dbs(self):
        self.make_cards_table()
        self.make_imgs_table()
        self.make_notes_table()


    def make_pages_table(self):
        """
        **layout hint**

        |page_number| text|
        |:---:|:----:|
        |45| lorem ipsum . . .|
        """
        pages_table = dbModel(
            db_folder=self.db_folder,
            db_name=self.safe_bookname,
            col_names=["page_number","value"],
            col_type=["TEXT","TEXT"]
        ) 

        self.tables["pages"] = pages_table

    def make_notes_table():
        """
        **layout hint**
        | page_number | sentence_number |value|
        |:--:|:--:|:--:|
        | page_45 | sentence_14 |this is some very important note for you|        
        """

    def make_imgs_table():
        """
        **layout hint**

        |page_number|img_number| value|
        |:--:|:--:|:--: |
        |73 | 2 | base64:|
        """




    def make_cards_table():


