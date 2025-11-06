import sys
import os
from secrets import token_urlsafe
from pypdf import PdfReader

sys.path.insert(0,r"c:/Users/ishall/Desktop/public_brainrootreader/brainrootreader/helpers")

from helpers.makebrr import PageTextHandler
from helpers.book_converter import ConvertFromPdf





def convert_book():
    """convert the pdf into the json file"""
    pdf_path = os.path.join(r"c:/Users/ishall/Desktop/public_brainrootreader/brainrootreader","uploads","this_is_marketing.pdf")
    book_data = PdfReader(pdf_path)


    temp = {}
    for i,page in enumerate(book_data.pages,start=1):
        text = page.extract_text()
        # probably gonna add image extraction here
        #imgs_handler.insert_imgs_by_page(page_number=i,imgs = page.images)

        if text != "":
            temp[i] = text




page_text_handler = PageTextHandler(
    base_path=r"c:/Users/ishall/Desktop/public_brainrootreader/brainrootreader",
    safe_bookname="testdb"
)

data = page_text_handler.get_text_of_page(page_number=15)
print(data)





