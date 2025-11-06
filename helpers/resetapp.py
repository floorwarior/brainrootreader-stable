"""
wipes the app clean

"""
import os 
from shutil import rmtree

def wipe_uploads_folder(base_path):
    upload_folder_path = os.path.join(base_path,"uploads")
    print(upload_folder_path)
    #
    # 
    rmtree(upload_folder_path)
        #os.remove(upload_folder_path)

    os.mkdir(upload_folder_path)



def reset_app(base_path):
    from helpers.remove_book import remove_doc
    from book_converter import get_booknames


    




    wipe_uploads_folder(base_path=)