import os
import numpy as np
from secrets import token_urlsafe
from abc import ABC, abstractmethod
try:
    from helpers.thepanic import Pan as pan
except:
    from thepanic import Pan as pan


import traceback
IS_BUILD = False

NoVoicesGetterError = "This reader does not support getting voices, make sure this is intended behavior."
NoSpeakerError = "This reader does not support speaking on this device, make sure this is intended behavior."
NoAudioSaveError = "This reader can not save audio, make sure this is intended behavior."


class BaseReader(ABC):


    def __init__(self,*args,speaker="there was no speaker specified",**kwargs):
        self.speaker = speaker
        self.imported_ok = False
        self.ready = True
        self.base_path = kwargs.get("base_path")
        self.origin = "builtin"
        self._on_speak_panic = lambda *args,**kwargs: print("speak has failed, default panic triggered because of:",kwargs.get("error"))
        self._on_audio_save_panic = lambda *args,**kwargs: print("audio save failed, defalt panic triggered because of error:",kwargs.get("error"))
        self.output_ending = "wav"
       
    
    def is_ready(self):
        return self.imported_ok and self.ready

    @abstractmethod
    def save_audio(self):
        """overwrite this to save the audio based on how the reader works"""
        pass

    @abstractmethod
    def Speak(self):
        """"""
        pass


    def get_voices(self,*args,**kwargs):
        """should return a maping to the voices, if you do not define it yourself it will always returns an empty dict"""
        return {}


    def on_audio_panic(self,*args,**kwargs):
        self._on_audio_save_panic(*args,**kwargs)



    def clean_up(self):
        """if you reader requires some kind of clean up this is what the server is calling before shutting down"""
        print("Reader clean up, not required")



    def on_speak_panic(self,*args,**kwargs):
        self._on_speak_panic(*args,**kwargs)





class WinReader(BaseReader):
    """ :param voice_index: int
        this is what you use to select a voice
    """

    def __init__(self, *args,speaker=None,voice_index=1,**kwargs):
        super().__init__( speaker=speaker,*args, **kwargs)
        try:
            import pythoncom
            from win32com.client import Dispatch
            pythoncom.CoInitialize()
            self.pythoncom = pythoncom
            self.imported_ok = True
            self.Dispatch = Dispatch
            self.speaker = Dispatch("SAPI.Spvoice")
            self.voice_index = voice_index
            self.model = kwargs.get("model")
            self.set_voices_by_index(self.model)
        
        except Exception as e:
            self.ready = False
            self.error = e
            print(e)



    def _make_thread_safe(self):
        self.pythoncom.CoInitialize()
        


    @pan.panic(on_panic="on_audio_panic",class_method=True)
    def Speak(self,*args,text,**kwargs):
        self._make_thread_safe()
        self.speaker.Speak(text)


    @pan.panic(on_panic="on_audio_panic",class_method=True)
    def save_audio(self,*args,**kwargs):
        self._make_thread_safe()
        page = kwargs.get("text")
        audio_out_name = kwargs.get("filename") 
        file_stream = self.Dispatch("SAPI.SpFileStream") 
        file_stream.Open(audio_out_name, 3, False)  # 3 = SSFMCreateForWrite
        self.speaker.AudioOutputStream = file_stream
        self.speaker.Speak(page)
        file_stream.Close()
        return audio_out_name


    def get_voices(self):
        voices = self.speaker.getVoices()
        voices_data = {}
        for j,v in enumerate(voices):
            voices_data[v.getDescription()] = str(j) 
        
        return voices_data


    def set_voices_by_index(self,index):
        self.speaker.Voice = self.speaker.getVoices()[int(index)]


class CoquiReader(BaseReader):

    def __init__(self, *args, speaker=None,model_folder="coquimodels",model="", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)
        try:
            import torch
            import sounddevice as sd
            self.sd = sd
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(device)            
            from TTS.api import TTS
            self.model = model
            self.tts = TTS(self.model).to(device)
            self.imported_ok = True
            self.ready = True
        except Exception as e:
            traceback.print_exc()
            self.imported_ok = False
            self.ready = False
            self.error = e


    def on_audio_panic(self, *args, **kwargs):
        return super().on_audio_panic(*args, **kwargs)



    @pan.panic(on_panic="on_audio_panic",class_method=True)
    def save_audio(self,*args,**kwargs):
        filename = kwargs.get("filename")
        text = kwargs.get("text")
        self.tts.tts_to_file(text=text,file_path = filename)
        return filename

    def Speak(self,*args,**kwargs):
        """speaks"""
        text = kwargs.get("text")
        wav = self.tts.tts(text)
        self.sd.play(wav, samplerate=self.tts.synthesizer.output_sample_rate)  # samplerate depends on the model
        self.sd.wait()


class PiperReader(BaseReader):



    def __init__(self, speaker=None,model="en_US-amy-medium.onnx",model_folder="pipermodels",*args,**kwargs):
        super().__init__(speaker=speaker,*args,**kwargs)
        try:
            self.base_path = kwargs.get("base_path",".")
            self.model_folder = os.path.join(self.base_path,model_folder)
            self.model = model
            from piper import PiperVoice
            import wave
            import sounddevice as sd
            self.sd = sd
            self.PiperVoice = PiperVoice
            self.voice = self.PiperVoice.load(os.path.join(self.model_folder,self.model),use_cuda=False)
            self.wave = wave
            self.imported_ok = True
        except Exception as e:
            self.ready = False
            self.error = e
            print(e)

    @pan.panic(on_panic="on_speak_panic",class_method=True)
    def Speak(self,text):
        stream = None
        for chunk in self.voice.synthesize(text):
            if chunk is None or not stream:  # First chunk
                sample_rate = chunk.sample_rate
                stream = self.sd.OutputStream(
                    samplerate=sample_rate,
                    channels=chunk.sample_channels,
                    dtype='int16'
                )
                stream.start()
            
            # Convert bytes to numpy array and play
            audio_array = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)
            stream.write(audio_array)

        if stream:
            stream.stop()
            stream.close()

    @pan.panic(on_panic="on_audio_save_panic",class_method=True)
    def save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        audio_out_name = kwargs.get("filename")
        

        with self.wave.open(audio_out_name, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file)

        return audio_out_name
    

    def get_voices(self):
        """gets all the voices in key value pairs where the key is the descriptor """
        models_files = os.listdir(self.model_folder)
        models = {}

        
        for i in models_files:
            if i.endswith(".onnx"):
                name_of_model = i 
                models[name_of_model] = name_of_model


        return models
    

class BrowserReader(BaseReader):
    """since it does not return anything it forces the system to use the browsers reader for audio"""
    def __init__(self, *args, speaker="browser reader", **kwargs):
        super().__init__(speaker=speaker, *args, **kwargs)
        self.imported_ok = True

    def Speak(self,*args,text="some text",**kwargs):
        return True
    

    def save_audio(self,*args,**kwargs):
        filenamme = kwargs.get("filename")
        return filenamme




class KokoroReader(BaseReader):
    """takes the following arguments: 
    - voice: str or path
    - lang_code: str

    - model: str or path <- *
    - config: str or path <- *
    - models_folder: str or path <-*
    - base_path: str <-*
    - g2p_model_folder : str or path  <-*
    *NOTE: these should be used only if you are trying to build the project, checkout my other repo for more info:
    https://github.com/floorwarior/pyinstaller_kokoro_build_guide
    example usege:
    ```
        reader = KokoroReader(
            voice="bm_daniel",
            lang_code="b"
    )
        reader.Speak(text="hello there")
    ```

    """
    def __init__(self, *args, speaker="kokoro", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)

        try:
            import soundfile as sf
            from kokoro import KPipeline,KModel
            import sounddevice as sd
            global IS_BUILD
            self.sf = sf
            self.sd = sd
            self.models_folder = kwargs.get("models_folder")
            self.base_path = kwargs.get("base_path")
            self._model = kwargs.get("model")
            self._voice = kwargs.get("voice") 
            self._config = kwargs.get("config") 
            self._model_path = None
            self._gp2_model_folder = None
            self.voice = self._voice
            if IS_BUILD:
                self._model_path =os.path.join(self.base_path,self.models_folder,self._model)
                self._gp2_model_folder = kwargs.get("g2p_model_folder")
                self.voice = os.path.join(self.base_path,self.models_folder,self._voice)

            # if you are building the script you will have to do some modifications to some of the classes see BUILDGUID.md
            # if you do not want to build the project you can use the precompiled releases
            #
            # self.pipeline = KPipeline(gp2_model_path=os.path.join(self.base_path,self._gp2_model_folder),lang_code=kwargs.get("lang_code"),model=KModel(
            #    model=os.path.join(self.base_path,self.models_folder,self._model),
            #    config=os.path.join(self.base_path,self.models_folder,self._config)))
            self.pipeline = KPipeline(lang_code=kwargs.get("lang_code"),model=KModel(
                model=self._model_path,
                config=self._config)
                )


            self.imported_ok = True
            self.ready = True
        except Exception as e:
            traceback.print_exc()
            self.imported_ok = False
            self.error = e

    def on_audio_save_panic(self,*args,**kwargs):
        if self._on_audio_save_panic:
            self._on_audio_save_panic(*args,**kwargs)



    @pan.panic(on_panic="on_audio_save_panic",class_method=True)
    def save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        audio_out_name = kwargs.get("filename")
        generator = self.pipeline(text,voice=self.voice)

        parts = []
        for i, (gs, ps, audio) in enumerate(generator):
            #print(i, gs, ps)
            #display(Audio(data=audio, rate=24000, autoplay=i==0))
            parts.append(audio)
            #sf.write(f'{i}.wav', audio, 24000)
        added = np.concatenate(parts)
        self.sf.write(audio_out_name,added,24000)

    @pan.panic(on_panic="on_speak_panic",class_method=True)
    def Speak(self,*args,**kwargs):
        text = kwargs.get("text")
        generator = self.pipeline(text,voice=self.voice)

        parts = []
        for i, (gs, ps, audio) in enumerate(generator):
            #print(i, gs, ps)
            #display(Audio(data=audio, rate=24000, autoplay=i==0))
            parts.append(audio)
            self.sd.play(audio, 24000)
            self.sd.wait()



readers = {
    "KokoroReader":KokoroReader,
    "PiperReader":PiperReader,
    "WinReader":WinReader,
    "BrowserReader":BrowserReader,
}
# TIP: if you are trying to make a custom build or want a faster stand up time, remove the readers you are not using


if __name__ == "__main__":
    reader = KokoroReader(
        voice="bm_daniel",
        lang_code="b"
    )
    reader.Speak(text="hello there")

    IS_BUILD = True

    reader = KokoroReader(
        voice="af_heart.pt"
        
    )
