import json
import os
from helpers.book_converter import get_booknames



def remove_bookname(base_path,safe_bookname):
    if not base_path:
        raise BaseException("remove_bookname did not recive a base_path")
    
    booklist_filename = os.path.join(base_path,"booklist.json")

    with open(booklist_filename,"r") as old_data:
        olddata = json.load(old_data)
        olddata.pop(safe_bookname.removesuffix("_readable.json"))

    with open(booklist_filename,"w") as new_data:
        json.dump(olddata,new_data,indent=4)


def remove_pdf(base_path,safe_bookname:str):
    """gets the real name of the book by looking it up first"""
    booknames = get_booknames(basepath=base_path)
    pdf_name = booknames.get(safe_bookname.removesuffix("_readable.json"),None)
    pdf_file_name = os.path.join(base_path,"uploads",f"{pdf_name}.pdf")
    if not os.path.exists(pdf_file_name):
        print("this pdf has been already removed from the system")
        return

    if not pdf_name:
        raise BaseException(f"your book with safe name: {safe_bookname} was not found it the records: {booknames}")
    os.remove(pdf_file_name)



def remove_doc(base_path,safe_bookname:str):
    """gets the real name of the book by looking it up first, then it removes its folders and the file associated with it"""
    booknames = get_booknames(basepath=base_path)
    doc_name = booknames.get(safe_bookname.removesuffix("_readable.json"),None)
    doc_file_name = os.path.join(base_path,"uploads",doc_name)
    if not os.path.exists(doc_file_name):
        print("this doc has been already removed from the system")
        return
    if not doc_name:
        raise BaseException(f"your book with safe name: {safe_bookname}, doc name: {doc_name} was not found it the records: {booknames}")
    os.remove(doc_file_name)
