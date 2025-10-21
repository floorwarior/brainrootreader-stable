from loadany import import_from_path
import os
test_folder = os.path.dirname(__file__)
project_folder = os.path.dirname(test_folder)
KokoroReader = import_from_path(os.path.join(project_folder,"helpers","bookreaders")).readers["KokoroReader"]
import os

if __name__ == "__main__":
    reader = KokoroReader(voice="af_heart",lang_code="a")
    reader.Speak(text="hello there")
    reader.save_audio(text="this is a test",filename=os.path.join(os.path.dirname(__file__),"testfile.wav"))
