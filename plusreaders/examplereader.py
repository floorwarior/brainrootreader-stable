from helpers.bookreaders import BaseReader
from abc import abstractmethod

class MyReader(BaseReader):

    def __init__(self, *args, speaker="there was no speaker specified", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)
        self.origin = "custom"

    def Speak(self,segment):
        print(segment)


    def save_audio(self,*args,**kwargs):
        page = kwargs.get("page")
        out_file_name = kwargs.get("filename")

        print(f"saving page: {page} at: {out_file_name}")



if __name__ == "__main__":
    reader = MyReader()
    reader.Speak("Hello there General Kenobi")
    reader.save_audio(filename="/static/bookname/or/tmp",page="it was a dark night, the sky crisp and clear, the stars were really bright")
