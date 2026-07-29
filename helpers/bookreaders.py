import os
#import numpy as np
from secrets import token_urlsafe
from abc import ABC, abstractmethod
try:
    from helpers.thepanic import Pan as pan
except:
    from thepanic import Pan as pan

import traceback
from helpers.binary_dependencies import BinaryDependencyNotFound,SOX,FFMPEG,ESPEAK_NG,BinaryDependency

IS_BUILD = False



class BaseReader(ABC):
    requirements = "requirements-[base].txt"
    dependencies = []
    recommended_python = "any"

    def __init__(self,*args,speaker="there was no speaker specified",**kwargs):
        self.error = None
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


    def check_binary_deps(self):
        """returns None on error return an error if there is a problem"""
        for d in self.dependencies:
            d: BinaryDependency 
            if not d.is_available():
                return d.geterror()
        return None
    
    def clean_up(self):
        """if you reader requires some kind of clean up this is what the server is calling before shutting down"""
        print("Reader clean up, not required")



    def on_speak_panic(self,*args,**kwargs):
        self._on_speak_panic(*args,**kwargs)





class WinReader(BaseReader):
    requirements = "requirements-[win-tts].txt"
    recommended_python = "any"

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
    #requirements = "requirements-[coqui-tts].txt" TODO
    # recommended_python = "3.10"
    dependencies = [ESPEAK_NG]


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
    requirements = "requirements-[piper-tts].txt"
    recommended_python = "any"
    dependencies = [ESPEAK_NG]


    def __init__(self, speaker=None,model="en_US-amy-medium.onnx",model_folder="pipermodels",*args,**kwargs):
        super().__init__(speaker=speaker,*args,**kwargs)
        try:
            self.base_path = kwargs.get("base_path",".")
            self.model_folder = os.path.join(self.base_path,model_folder)
            self.model = model
            from piper import PiperVoice
            import wave
            import sounddevice as sd
            import numpy as np
            self.np = np
            self.sd = sd
            self.PiperVoice = PiperVoice
            self.voice = self.PiperVoice.load(os.path.join(self.model_folder,self.model),use_cuda=False)
            self.wave = wave
            deps_not_okay = self.check_binary_deps()
            if deps_not_okay:
                raise deps_not_okay
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
            audio_array = self.np.frombuffer(chunk.audio_int16_bytes, dtype=self.np.int16)
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
        raise Exception("BrowserReader has been depricated, it does not work with the current logic")
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
    requirements = "requirements-[kokoro-tts].txt"
    recommended_python = "any"
    dependencies = [ESPEAK_NG]


    def __init__(self, *args, speaker="kokoro", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)

        try:
            import soundfile as sf
            import numpy as np
            from kokoro import KPipeline,KModel
            self.KPipeline = KPipeline
            import sounddevice as sd
            global IS_BUILD
            self.sf = sf
            self.sd = sd
            self.np = np
            self.models_folder = kwargs.get("models_folder")
            self.base_path = kwargs.get("base_path")
            self._model = kwargs.get("model")
            self._voice = kwargs.get("voice") 
            self._config = kwargs.get("config") 

            self.config = None
            self.model_path = None
            self.g2p_model_folder = None
            self.voice = self._voice
            if IS_BUILD:
                self.model_path =os.path.join(self.base_path,self.models_folder,self._model)
                self._g2p_model_folder = kwargs.get("g2p_model_folder")
                self.g2p_model_folder =  os.path.join(self.base_path,self._g2p_model_folder)
                self.voice = os.path.join(self.base_path,self.models_folder,self._voice)
                self.config = os.path.join(self.base_path,self.models_folder,self._config)
                # if you are building a custom exe, read this guide first: https://github.com/floorwarior/pyinstaller_kokoro_build_guide
                self.pipeline = KPipeline(lang_code=kwargs.get("lang_code"),model=KModel(
                    model=self.model_path,
                    config=self.config,
                    ),g2p_model_path =self.g2p_model_folder
                    )
            else:
                self.pipeline = KPipeline(lang_code=kwargs.get("lang_code"))

            deps_not_okay = self.check_binary_deps()
            if deps_not_okay:
                raise deps_not_okay

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
        generator = self.pipeline(text,voice=self.voice, speed=1, split_pattern=r'\n+')

        parts = []
        for i, (gs, ps, audio) in enumerate(generator):
            #print(i, gs, ps)
            #display(Audio(data=audio, rate=24000, autoplay=i==0))
            parts.append(audio)
            #sf.write(f'{i}.wav', audio, 24000)
        added = self.np.concatenate(parts)
        self.sf.write(audio_out_name,added,24000)
        return audio_out_name

    @pan.panic(on_panic="on_speak_panic",class_method=True)
    def Speak(self,*args,**kwargs):
        text = kwargs.get("text")
        generator = self.pipeline(text,voice=self.voice, speed=1, split_pattern=r'\n+')
        parts = []
        for i, (gs, ps, audio) in enumerate(generator):
            #print(i, gs, ps)
            #display(Audio(data=audio, rate=24000, autoplay=i==0))
            parts.append(audio)
            self.sd.play(audio, 24000)
            self.sd.wait()



    def get_voices(self):
        """gets the currently downloaded voices"""
        if IS_BUILD:
            voices = [file for file in self.models_folder if file.endswith(".pt")]
            items = {
            }
            for voice in voices:
                items[voice.removesuffix(".pt")] = voice
            return items
        else:
            return {}
        


class QwenTTSReader(BaseReader):
    requirements = "requirements-[qwen-tts].txt"
    recommended_python = "3.11"


    def __init__(self, *args,  **kwargs):
        super().__init__(self,*args,**kwargs)
        self.error = "no error"
        try:
            import torch
            from qwen_tts import Qwen3TTSModel
            import soundfile as sf
            import sounddevice as sd
            self.sf = sf
            self.sd = sd
            self.imported_ok = True
            self.speaker = kwargs.get("speaker","Ryan")
            self.model =  Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
                device_map="cuda:0",
                dtype=torch.bfloat16,
            )
            deps_not_okay = self.check_binary_deps()
            if deps_not_okay:
                raise deps_not_okay
            self.ready = True
        except Exception as e:
            self.error = e
            print(self.error)

    def Speak(self,*args,**kwargs):
        text = kwargs.get("text")
        wavs,sr = self.model.generate_custom_voice(
            text=text,
            speaker="Ryan",
        )

        for wv in wavs:
            self.sd.play(wv, samplerate=sr)  # samplerate depends on the model
            self.sd.wait()

    def save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        audio_out_name = kwargs.get("filename")
        # single inference
        wavs, sr = self.model.generate_custom_voice(
            text=text,
            speaker=self.speaker,
        )
        self.sf.write(audio_out_name, wavs[0], sr)


class PocketTTSReader(BaseReader):
    requirements = "requirements-[pocket-tts].txt"
    recommended_python = "any"
    def __init__(self, *args, **kwargs):
        super().__init__(self,*args,**kwargs)
        try:
            from pocket_tts import TTSModel
            import scipy.io.wavfile as wavefile
            import sounddevice as sd
            self._tts_model = TTSModel
            self.wavefile = wavefile
            self.imported_ok = True
            self.tts_model = self._tts_model.load_model()
            self.sd = sd
            self.voice_state = self.tts_model.get_state_for_audio_prompt(

    kwargs.get("voice")  # One of the pre-made voices, see above
    # You can also use any voice file you have locally or from Hugging Face:
    # "./some_audio.wav"
    # or "hf://kyutai/tts-voices/expresso/ex01-ex02_default_001_channel2_198s.wav"
)
        except Exception as e:
            print(f"[FAILED WITH {e}]")
            self.error = e
            self.imported_ok = False

    
    def Speak(self,*args,**kwargs):
        text = kwargs.get("text")
        audio = self.tts_model.generate_audio(model_state=self.voice_state,text_to_generate=text,max_tokens=100)
        wav = audio.numpy()      # tensor -> numpy
        self.sd.play(wav,self.tts_model.sample_rate)
        self.sd.wait()

    def save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        audio_out_name = kwargs.get("filename")
        audio = self.tts_model.generate_audio(model_state=self.voice_state,text_to_generate=text,max_tokens=100)
        self.wavefile.write(audio_out_name,self.tts_model.sample_rate,audio.numpy())


class F5TTSReader(BaseReader):
    requirements = "requirements-[f5-tts].txt"
    recommended_python = "3.11"
    dependencies = [FFMPEG]

    def __init__(self, *args, speaker="there was no speaker specified", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)
        try:    
            from f5_tts.api import F5TTS
            import sounddevice as sd
            import soundfile as sf

            self.ref_text = kwargs.get("ref_text")
            self.ref_file = kwargs.get("ref_file")
            self.seed = None
            self.sd = sd
            self.sf = sf
            self.tts = F5TTS()
            deps_not_okay = self.check_binary_deps()
            if deps_not_okay:
                raise deps_not_okay


            self.ready = True
            self.imported_ok = True

        except Exception as e:
            print(e)
            self.error = e



    def Speak(self,*args,**kwargs):
        text = kwargs.get("text")

        seed = None
        if self.seed:
            seed = self.seed


        wav, sr, spec = self.tts.infer(
            ref_text=self.ref_text,
            ref_file=self.ref_file,
            gen_text=text,
            seed=seed,
        )

        self.seed = self.tts.seed
        self.sd.play(wav, samplerate=sr)
        self.sd.wait()

        

    def save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        audio_out_name = kwargs.get("filename")

        seed = None
        if self.seed:
            seed = self.seed

        wav, sr, spec = self.tts.infer(
            ref_text=self.ref_text,
            ref_file=self.ref_file,
            gen_text=text,
            file_wave="f5_test.wav",
            seed=seed,
        )

        self.seed = self.tts.seed

        self.sf.write(audio_out_name, wav,sr)
        return audio_out_name
    

class ChatterBoxTTSReader(BaseReader):
    """
    ref_audio: path    
    device: str ["cuda","cpu"]
    """
    requirements = "requirements-[chatterbox-tts].txt"
    recommended_python = "3.12"


    def __init__(self, *args, speaker="there was no speaker specified", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)
        try:   
            import torchaudio as ta
            import torch
            from chatterbox.tts_turbo import ChatterboxTurboTTS
            import sounddevice as sd
            deps_not_okay = self.check_binary_deps()
            if deps_not_okay:
                raise deps_not_okay


            self.ta = ta
            self.sd = sd
            self.ref_audio_path = kwargs.get("ref_audio")
            # Load the Turbo model
            self.tts = ChatterboxTurboTTS.from_pretrained(device=kwargs.get("device","cpu")) # should return cuda or cpu
            

           
            self.ready = True
            self.imported_ok = True

        except Exception as e:

            self.ready = False
            self.imported_ok = False
            self.error = e


    def save_audio(self,*arg,**kwargs):
        text = kwargs.get("text")
        audio_out_name = kwargs.get("filename")

        wav = self.tts.generate(
            text=text,
            audio_prompt_path=self.ref_audio_path
        )

        self.ta.save(audio_out_name, wav, self.tts.sr)
        return audio_out_name

    def Speak(self,*args,**kwargs):
        text = kwargs.get("text")




        wav = self.tts.generate(
            text=text,
            audio_prompt_path=self.ref_audio_path
        )

        wav = wav.squeeze(0)          # [1,43200] -> [43200]
        wav = wav.cpu().numpy()      # tensor -> numpy



        #wav = wav.cpu().numpy()

        self.sd.play(wav,self.tts.sr)
        self.sd.wait()

class SupertonicReader(BaseReader):
    requirements = "requirements-[supertonic].txt"
    recommended_python = "any"

    def __init__(self, *args, speaker="there was no speaker specified", **kwargs):
        super().__init__(*args, speaker=speaker, **kwargs)
        # TODO make the config load stuff
        try:
            from supertonic import TTS
            import sounddevice as sd

            # First run downloads the model from Hugging Face automatically.
            self.steps = int(kwargs.get("steps"))
            self.speed = float(kwargs.get("speed"))
            self.lang = kwargs.get("lang")
            self.style_ = kwargs.get("style")

            self.sd = sd
            self.tts = TTS(auto_download=True)
            self.style = self.tts.get_voice_style(voice_name=self.style_)


            deps_not_okay = self.check_binary_deps()
            if deps_not_okay:
                raise deps_not_okay

            self.imported_ok = True
            self.ready = True


        except Exception as e:
            print(f"[ FAILED WITH: {e}]")
            self.ready = False
            self.imported_ok = False
            self.error = e

    def Speak(self,*args,**kwargs):
        text = kwargs.get("text")

        wav, duration = self.tts.synthesize(
            text=text,
            lang=self.lang,                      # Language code (e.g., "en", "ko", "na" for language-agnostic)
            voice_style=self.style,              # Voice style object
            total_steps=self.steps,                  # Quality: 5 (low) to 12 (high), default 8 (medium)
            speed=self.speed         # Speed: 0.7 (slow) to 2.0 (fast)
        )
        
        wav = wav.squeeze()

        self.sd.play(wav,self.tts.sample_rate)
        self.sd.wait()


    def save_audio(self,*args,**kwargs):
        text = kwargs.get("text")
        filename = kwargs.get("filename")
        wav, duration = self.tts.synthesize(
            text=text,
            lang=self.lang,                      # Language code (e.g., "en", "ko", "na" for language-agnostic)
            voice_style=self.style,              # Voice style object
            total_steps=self.steps,                  # Quality: 5 (low) to 12 (high), default 8 (medium)
            speed=self.speed         # Speed: 0.7 (slow) to 2.0 (fast)
        )
        self.tts.save_audio(output_path=filename,wav=wav)

readers = {
    "KokoroReader":KokoroReader,
    "PiperReader":PiperReader,
    "WinReader":WinReader,
    "QwenTTSReader":QwenTTSReader,
    "F5TTSReader":F5TTSReader,
    "ChatterBoxTTSReader":ChatterBoxTTSReader,
    "PocketTTSReader":PocketTTSReader,
    "SupertonicReader":SupertonicReader
}

# TIP: if you are trying to make a custom build or want a faster stand up time, remove the readers you are not using


if __name__ == "__main__":

    reader = QwenTTSReader(
    )
    reader.save_audio(text="What's up suckers?",filename="suckers.wav")
