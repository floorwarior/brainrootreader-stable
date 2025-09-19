"""contains all the links for the models the code curls the selected models from the site
"""
import requests
import os
import json


class VoiceStoreBase():


    def __init__(self,name,base_path,model_folder_foldername,baseendpoint,voicesendpoint):
        self.name = name
        self.base_endpoint = baseendpoint
        self.voices_endpoint = voicesendpoint  
        self.base_path = base_path
        self.model_folder_filename = model_folder_foldername
        """**NOT A PATH**"""
        self.model_folder = os.path.join(self.base_path,self.model_folder_filename)
        """**IS A PATH**"""
        self.voices_data_json = None
        self.get_cached_voices()

    def get_store_voices(self):
        """requests the json that stores the voices for the reader"""
        self.voices_data_json = requests.get(self.voices_endpoint).json()
        # updates the voices.json in the model folder
        self.online_voice_list_file = os.path.join(self.model_folder,"voices.json")
        with open(self.online_voice_list_file,"w") as new_online_voices:
            json.dump(self.voices_data_json,new_online_voices,indent=4)


        return self.voices_data_json
        """data example from json:  "ca_ES-upc_ona-medium": {
        "key": "ca_ES-upc_ona-medium",
        "name": "upc_ona",
        "language": {
            "code": "ca_ES",
            "family": "ca",
            "region": "ES",
            "name_native": "Català",
            "name_english": "Catalan",
            "country_english": "Spain"
        },
        "quality": "medium",
        "num_speakers": 1,
        "speaker_id_map": {},
        "files": {
            "ca/ca_ES/upc_ona/medium/ca_ES-upc_ona-medium.onnx": {
                "size_bytes": 63201294,
                "md5_digest": "58ff3b049b6b721a4c353a551ec5ef3a"
            },
            "ca/ca_ES/upc_ona/medium/ca_ES-upc_ona-medium.onnx.json": {
                "size_bytes": 4875,
                "md5_digest": "035e9eb642ab9fa1354f53a77877ae9b"
            },
            "ca/ca_ES/upc_ona/medium/MODEL_CARD": {
                "size_bytes": 296,
                "md5_digest": "395c782a56632400f46e7c442c7718bb"
            }
        },
        "aliases": []
        """

    def get_cached_voices(self):
        """returns the already downloaded voices list from the models folder, if not needed this should not be refreshed much there is not real reason"""
        online_voice_list_file = os.path.join(self.model_folder,"voices.json") 
        if not os.path.exists(online_voice_list_file):
            not_cached = self.get_store_voices()
            self.voices_data_json = not_cached
            return not_cached        
        with open(online_voice_list_file,"r") as cached_voice_list:
            cached = json.load(cached_voice_list)

        return cached

    def download_voice(self,keyofvoice):
        """grabs the voice form the endpoint and downloads it into the correct folder"""

        from urllib.parse import urljoin 
        if not self.voices_data_json:
            self.get_store_voices()
        uniqueid = keyofvoice.replace("/","_")


        voice_data = self.voices_data_json[keyofvoice]["files"]
        for file in voice_data.keys():
            url = urljoin(self.base_endpoint,file)
            filename = file.rsplit("/")[-1]
            if filename == "MODEL_CARD":
                filename = f"{uniqueid}_MODEL"
            response = requests.get(url)
            with open(os.path.join(self.model_folder,filename), "wb") as f:
                f.write(response.content)

class VoiceStorePiper(VoiceStoreBase):

    def __init__(self, name, base_path, model_folder_foldername, baseendpoint, voicesendpoint):
        super().__init__(name, base_path, model_folder_foldername, baseendpoint, voicesendpoint)



if __name__ == "__main__":
    print( os.path.dirname(os.path.dirname(__file__)),)
    piper_voice_store = VoiceStorePiper(
            name="Piper",
            base_path=os.path.dirname(os.path.dirname(__file__)),
            model_folder_foldername="pipermodels",
            baseendpoint="https://huggingface.co/rhasspy/piper-voices/resolve/main/",
            voicesendpoint="https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
        )
    piper_voice_store.download_voice("en_US-amy-medium")
    #piper_voice_store.download_voice("ed_US-amy-medium")
