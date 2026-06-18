"""Allows you to define new themes for BRR"""
from dataclasses import dataclass

@dataclass
class Theme():
    home : str
    settings: str
    voicebag: str
    test_image_quality: str
    add_video : str
    read_book: str
    convert_book_to_audio :str
    shutdownscreen: str



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
    )
}

def register_custom_theme(name,data):
    THEMES[name] = Theme(**data)




