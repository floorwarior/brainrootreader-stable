import sys
import os
from secrets import token_urlsafe
from pypdf import PdfReader
import secrets

BASE_PATH = os.getcwd()
sys.path.insert(0,r"c:/Users/ishall/Desktop/public_brainrootreader/brainrootreader/helpers")

from helpers.makebrr import NotesHandler

import unittest

class TestNotesHandler(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)


    def test_the_flow(self):
        brr_path = os.path.join(BASE_PATH,"static","books","brr_testdb.brr")
        if os.path.exists(brr_path):
            os.remove(brr_path)
        notes_handler = NotesHandler(
            base_path=BASE_PATH,
            safe_bookname="testdb"
        )
        notes_handler.add_note(
            note="This is a test",
            sentence_number=2,
            page_number=4
        )
        data = notes_handler.get_notes_of_page(page_number=4)

        notes_handler.change_note(
            note_id=data[2][0]["note_id"],
            new_note="This is also a test"
        )


        data = notes_handler.get_notes_of_page(page_number=4)
        #print(" This is the data", data)
        assert data[2][0]["note"] == "This is also a test" , "Updating the note does not work" # 4 is a key, 0 is an index inside the list



        notes_handler.remove_note(note_id=data[2][0]["note_id"])

        data = notes_handler.db.find_where(col_name=["note"],conditions=["note_id = ?"],values=[data[2][0]["note_id"]],getall=False)
        print(data)

        os.remove(brr_path)
        return self.assertEqual(data,{}, "note was not deleted from the database")


if __name__ == "__main__":
    unittest.main()

