


from helpers.bookreaders import BaseReader



class ThisIsTest(BaseReader):

    def __init__(self,reader="test reader",*args,**kwargs):
        super().__init__(self,reader)
        self.origin = "custom"


    def Speak(self,text):
        print("this is Speak")


    def save_audio(self):
        print("this is save_audio")


