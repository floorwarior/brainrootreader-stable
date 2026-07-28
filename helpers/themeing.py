"""Allows you to define new themes for BRR"""
from dataclasses import dataclass

@dataclass
class Theme():
    home : str = None
    settings: str = None
    voicebag: str = None
    test_image_quality: str = None
    add_video : str = None
    read_book: str = None
    convert_book_to_audio :str = None
    shutdownscreen: str = None


THEMES = {
    "OLD_THEME" : Theme(
        home="index_v2.html",
        voicebag="voicebag.html",
        settings="settings.html",
        test_image_quality="testimage_v2.html",
        add_video="uploadvideo.html",
        convert_book_to_audio = "convertingbooktoplaylist.html",
        read_book="readpage_v3.html",
        shutdownscreen="shutdownscreen.html"
    ),"NEW_THEME":Theme(
        home="landing.html",
        read_book="reading.html",
        settings="settings.html" ,
        shutdownscreen="shutdownscreen.html",
        convert_book_to_audio="convert_to_audio.html" 
    )
}




def register_custom_theme(name,data):
    THEMES[name] = Theme(**data)




