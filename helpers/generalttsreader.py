
import os
import nltk
from nltk import sent_tokenize
import json
import pypdf
from functools import lru_cache

try:
    from helpers.book_converter import return_cache
    from helpers.remove_book import remove_bookname,remove_doc
    from helpers.book_converter import update_booknames
except:
    from book_converter import return_cache
    from book_converter import update_booknames


import secrets


always_delete_tmp = False



class ReadBook():
    def __init__(self,safe_bookname:str=None,starting_page=0,base_path_=None,og_bookname=None,reader_=None,alias_=None,pdf_path=None):
        # pulls the first available reader no reader is specified or 
        try:
            if reader_:
                self.reader = reader_
                if not reader_.is_ready():
                    print(reader_.error)
                    raise BaseException(f"reader: {reader_.__class__.__name__}, did not initialize correctly, switching to backups")
                print(f"[GLOBAL READER {self.reader.__class__.__name__} IS READY TO USE]")
            else:
                raise BaseException("no reader was specified,assigning one automaticly")
        except BaseException as e:
            print(e)
            self.reader = self.pull_fallback_reader(base_path=base_path_)
        
        self.og_bookname = og_bookname
        self.base_path = base_path_
        self.upload_folder = os.path.join(self.base_path,"uploads")
        """is a PATH"""
        self.static_folder = os.path.join(self.base_path,"static")
        """is a PATH"""

        print(self.base_path)
        print(self.upload_folder)
        print(self.static_folder)
        if not safe_bookname:
            if not pdf_path or not self.og_bookname:
                raise BaseException("no book provided")
            self.safe_bookname = self.process_pdf(pdf_path) # proccess pdf makes the folder for the book
        else:
            self.safe_bookname = safe_bookname
        self.book_name = safe_bookname 

        self.alias_name = None if not alias_ else alias_ #this is used later for metadata and playlist naming




        self.books_folders_name = self.safe_bookname.removesuffix("_readable.json")
        """only the name of the folder **NOT a PATH**,"""
        self.books_folder = os.path.join(self.static_folder,"books",self.books_folders_name)
        """this is the folder that is holding all the data of the book, has tmp and the audio files, **IS a PATH** and can be used as such"""
        self.temp_folder = os.path.join(self.books_folder,"tmp")
        """holds the senteces data, **IS A PATH**"""
        # json file, contains all the page data:
        self.this_books_json = os.path.join(self.static_folder,"books",self.safe_bookname)
        """point to the file that holds all the page data by keys, **IS A PATH**"""
        if not os.path.exists(self.books_folder):os.makedirs(self.books_folder)
        self.starting_page : int  = starting_page
        self.playlist_file_name = os.path.join(self.books_folder,"playlist.m3u")
        # hooks:
        self._on_page_progress = lambda *args,**kwargs: print("current page is:",kwargs.get("page"),"page_num:",kwargs.get("page_num"))
        """automaticly gets the page : str , and page_num: int values"""
        self._on_sentence_progress = lambda *args,**kwargs: print("current sentence is:",kwargs.get("sentence"),"current_sentence_num:",kwargs.get("sentence_num"))
        """automaticly get the sentence :str and the sentecne_num values"""
        self._on_conversion_finished = lambda *args,**kwargs: print("conversion of your book is complete")
        # error hooks
        self._on_catastrofic_audio_failiure = lambda *args,**kwargs: print("complete audio failiure, your audio did not save",kwargs.get("error")) or True
        """gets passed the error argument that you can use to see what went wrong"""
        self._on_catastrofic_speaker_failiure = lambda *args,**kwargs: print("complete speaker failiure,",kwargs.get("error")) or True
        """gets passed the error argument that you can use to see what went wrong"""
        # output ending
        self.output_ending = self.reader.output_ending
        self.first_page_last_page()



    @staticmethod
    def pull_fallback_reader(base_path=None,*args,**kwargs):
        """if no read was specified it will try to select a reader until one works
        It uses the GLOBALREADERCONFIG['fallbakorder'] : attribute
        you can modify this in the file@::readerconfigs/globalreader folder


        """
        from helpers.bookreaders import readers as builtin_readers
        from plusreaders import readers as plusreaders
        from helpers.loadreader import get_readers_config
        all_readers = {**builtin_readers,**plusreaders}
        from readerconfigs import GLOBALREADERCONFIG

        for reader in GLOBALREADERCONFIG["fallbackorder"]:
            fallbackreader_class = all_readers[reader]
            fallbackreader_config = get_readers_config(base_path,fallbackreader_class.__name__)
            fallbackreader = fallbackreader_class(**fallbackreader_config)
            if fallbackreader.is_ready():
                print(f"[ FALLBACK READER: {fallbackreader.__class__.__name__} ]")
                return fallbackreader

        raise BaseException("none of the readers are supported this means the readbook class is unuseable")


    def load_snapshot_reader(self):
        """gets the reader form the snapshoted settings"""
        raise NotImplementedError("this functionality has not been implemented yet")


    def _make_folders(self):
        """checks to see if the important folders are present or not and creates them if they are not present"""
        folders = [self.upload_folder,self.books_folder]
        for f in folders:
            if not os.path.exists(f):
                os.mkdir(f)



    def first_page_last_page(self):
        """
        set the first and last page attributes so you can use these elsewhere
        """
        book_, success = return_cache(basepath=self.base_path,safe_bookname=self.safe_bookname)
        if not success:
            return "Book was not converted before"
        keys = list(book_.keys())
        self.first_page = int(keys[0])
        self.last_page = int(keys[-1])


    def page_count(self):
        """retunrs how many pages your book has"""
        book_ ,data = return_cache(basepath=self.base_path,safe_bookname=self.safe_bookname)
        return len(book_.keys())


    def delete_book(self):
        """removes the book from the booklist, removes the uploaded pdf,"""
        import shutil
        shutil.rmtree(self.books_folder)
        remove_doc(base_path=self.base_path,safe_bookname=self.safe_bookname)
        remove_bookname(base_path=self.base_path,safe_bookname=self.safe_bookname)
        os.remove(self.this_books_json)
        return True


    def process_pdf(self,pdf_path):
        """takes the pdf converts it, makes the folder for the pdf, and also makes the json
        deprecated        
        """
        book = pypdf.PdfReader(pdf_path)
        page_data = {}
        for page_num ,page in enumerate(book.pages):
            page_data[page_num] = page.extract_text()

        safe_book_name = secrets.token_urlsafe(32)

        books_folder = os.path.join(self.static_folder,"books",safe_book_name)
        if not os.path.exists(books_folder):
            os.mkdir(books_folder)

        with open(os.path.join(self.static_folder,"books",f"{safe_book_name}_readable.json"),"w") as newbookfile:
            json.dump(page_data,newbookfile,indent=4)


        update_booknames(safe_book_name,self.og_bookname,basepath=self.base_path)
        return safe_book_name



    def update_playlist(self,pages):
        """takes all the pages and updates what pages we have already"""
        playlist_file_name = os.path.join(self.books_folder,"playlist.m3u")
        with open(playlist_file_name,"a+") as f:
            for p in pages:
                f.write(p)
                f.write("\n")



    def make_playlist(self,pages):
        """used if there is no existing playlist present already"""
        playlist_filename = os.path.join(self.books_folder,"playlist.m3u")

        with open(playlist_filename,"a+") as f:
            f.write("#EXTM3U")
            for p in pages:
                f.write(p)
                f.write("\n")


    def fix_playlist(self):
        """lists all the files in the folder and makes a playlist"""
        if not os.path.exists(self.playlist_file_name):
            audio_files = os.listdir(self.books_folder)
            pages_data = []
            for f in sorted(audio_files,key=lambda x:int(x.removeprefix("page_").removesuffix(f".{self.output_ending}")) ):
                pages_data.append(f)
            self.make_playlist(pages=pages_data)
        else:
            return "audio file already exists"

    
    def books_data(self):
        return return_cache(self.book_name,basepath=self.base_path)


    def read_segment(self,text):
        self.reader.Speak(text)




    def save_one_page(self,page):
        """check to see if the specific page is already converted or not and returns the name in the end"""
        page_name = f"page_{page}.{self.output_ending}"
        page_filename = os.path.join(self.books_folder,page_name)

        if not os.path.exists(page_filename):
            self.reader.save_audio(text=page,filename=page_filename)


        return page_filename
    

    def remove_snapshot_config(self):
        """
        Removes the config of the snapshot
        """
        # books config file
        books_config = os.path.join(self.books_folder,"settings_config.json")
        if os.path.exists(books_config):
            os.remove(books_config)


    def snapshot_config(self):
        """
        - Makes a config file of the current settings
        - places it into the books folder
        - this way if you jump a lot between books like hungarian, english  whatever, it will change its lang automaticly
        """
        raise NotImplementedError("i did not add this functionality just yet")






    def save_transscript_for_page(self,page_num):
        """breaks the page into a sentence"""
        data, _ = self.books_data()
        filenames = []
        sentences  =  sent_tokenize(data.get(str(page_num)))

        for s in range(len(sentences)):
            filenames.append(f"/static/books/{self.books_folders_name}/tmp/page_{page_num}_sentence_{s}.{self.output_ending}")

        book_data = {}

        y = 0
        for sentence,val in zip(sentences,filenames):
            book_data[str(y)] = {"sentence":sentence,"filename":val}
            y+=1
        #print(book_data)
        return book_data


    def reset_tmp_folder(self):
        files = os.listdir(self.temp_folder)
        for f in files:
            os.remove(os.path.join(self.temp_folder,f))



    def alreadyconverted(self,filename):
        """
        check if the page was converted before and return true if it was
        """
        return os.path.exists(filename)


    def save_page_by_sentences(self,page_number):
        """
        **SAVES the page in the temporary folder**
        """

        book,success = self.books_data()
        page = book[str(page_number)]
        if not success:
            raise BaseException("this book was not coverted before, make sure to convert it first")
        sentences = sent_tokenize(page)

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
        else:
            if always_delete_tmp:
                self.reset_tmp_folder()

        for i,s in enumerate(sentences):
            filename = os.path.join(self.temp_folder,f"page_{page_number}_sentence_{i}.{self.output_ending}")
            if not self.alreadyconverted(filename):
                self.reader.save_audio(text=s,filename=filename)
            self.on_sentence_progress(sentence=s,sentence_num=i)

        return True


    def on_page_progress(self,*args,**kwargs):
        """gets called each time you finish a page conversion"""
        if self._on_page_progress:
            self._on_page_progress(*args,**kwargs)
        

    def on_sentence_progress(self,*args,**kwargs):
        """gets called each time a sentence is finished"""
        if self._on_sentence_progress:
            self._on_sentence_progress(*args,**kwargs)


    def on_conversion_finished(self,*args,**kwargs):
        """gets called once the whole book has been converted"""
        if self._on_conversion_finished:
            self._on_conversion_finished(*args,**kwargs)
            


    def remove_last_audio(self):
        """removes the last converted file before continuing conversion, this is done so there is no corrupted audio"""
        page = f"page_1.{self.reader.output_ending}"
        current = self.first_page
        while os.path.exists(os.path.join(self.books_folder,self.books_folders_name,page)) and current <= self.last_page:
            current += 1
            page = f"page_{current}.{self.reader.output_ending}"
        audio_path = os.path.join(self.books_folder,page)
        print("removing:",audio_path)
        if os.path.exists(audio_path):
            print("removing: ", audio_path)
            os.remove(audio_path)


    def read_page_by_sentence(self,page):
        sentences = sent_tokenize(page)
        for sentence in sentences:
            self.reader.Speak(text=sentence)

    def read_book(self,save=False):
        book_data,success = self.books_data()
        pages = []
        if not success:
            return "no such book converted before"
        self.remove_last_audio()
        
        for page_num,page in list(book_data.items())[self.starting_page:]:
            if page == "":
                continue
            print(f"[ READING PAGE: {page_num} ]")
            if not save:
                self.read_page_by_sentence(page)
            else:
                pagename = self.save_audio(page=page,page_number=page_num)
                if pagename:
                    pages.append(pagename)
                else:
                    print(f"[ page: {page_num} already exists ]")

            self.on_page_progress(page=page,page_num=page_num)
            
        self.on_conversion_finished(book_folder=self.books_folder)

        if os.path.exists(self.playlist_file_name):
            self.update_playlist(pages)
        else:self.make_playlist(pages)





    def save_audio(self,page,page_number):
        """based on which reader it is using it saves the audio"""
        pagename = f"page_{page_number}.{self.output_ending}"
        if os.path.exists(os.path.join(self.books_folder,pagename)):
            return False
        filename = os.path.join(self.books_folder,pagename)
        self.reader.save_audio(text=page,filename=filename)

        return pagename


    def zipbookfolder(self):
        """makes the folder into a zip file that can be downloaded from the server"""
        import shutil
        zip_filename = os.path.join(self.books_folder,f"{self.books_folders_name}.zip")
        if os.path.exists(zip_filename):
            if not input("you already compiled this book, do you want to coninue? | y | n |").lower() == "y":
                return False
        else:
            shutil.make_archive(zip_filename,'zip',self.books_folder)


if __name__ == "__main__":
    rd = ReadBook(og_bookname="This is marketing",pdf_path=r"c:/Users/ishall/Downloads/this is marketing.pdf",starting_page=168,base_path_=os.getcwd())
    rd.read_book(save=False)
