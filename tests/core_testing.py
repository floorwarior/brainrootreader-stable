from loadany import import_from_path
import os 
test_folder = os.path.dirname(__file__)
project_folder  = os.path.dirname(test_folder)
moduls_folder = "helpers"
tested_file = "readercore_connector_v2.py"

ReaderCoreConnector = import_from_path(file_path=os.path.join(project_folder,moduls_folder,tested_file)).ReaderCoreConnector

if __name__ == "__main__":
    reader = ReaderCoreConnector(
        core_count="1",
    )
    reader.Speak(text="this is a really important text here")
    reader.save_audio(filename=os.path.join(test_folder,"test.wav"),text="Hello there general kenobi")
    import time
    time.sleep(10)
    reader.clean_up()
