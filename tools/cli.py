

try:        
    import click
    import questionary
    import os
    import subprocess
    import shutil
    import datetime
    import sys
    import time
    import platform

    from helpers.bookreaders import readers
    from plusreaders import readers as plusreaders
    from helpers.loadreader import load_reader,get_readers_config
    from helpers.increment_port import get_next_port
    from helpers.dedicated_venv import is_venv,remove_venv,make_dedicated_venv,venv_name
    from helpers.readercore_connector_v2 import ReaderCoreConnector


    readers.update(plusreaders)
    start_port = get_next_port(4222,1)


except Exception as e:
    print(
"""you do not have the dependencies installed:
first run this:
python.exe -m venv .venv
# then this:
.venv\\Scripts\\activate
# finally:
pip install -r requirements-[base].txt -r requirements-[cli].txt
""")
    exit()

def reader(ignore_venv):
    base_path = questionary.path(message="what is the root of your project?").ask()
    questions = [
    {
        "type": "select",
        "name": "reader",
        "message": "Select Reader",
        "choices": [*list(readers.keys())],
    },
    {
        "type":"select",
        "name":"mode",
        "message":"Select Mode",
        "choices":["speak","save audio","benchmark","install-in-dedicated-venv","install-in-current-venv","exit","remove-current-venv","remove-dedicated-venv"]
    }
    ]

    answers = questionary.prompt(questions=questions)
    READER = readers[answers['reader']]
    CONFIG = get_readers_config(base_path=base_path,readername=answers["reader"])
    
    def get_reader():
        if is_venv(base_path=base_path,reader=READER) and not ignore_venv:
            rd = ReaderCoreConnector(
                base_path=base_path,
                is_frozen = False,
                core_count = "1",
                forced_reader = READER.__name__
            )
            return rd
        else:
            rd = READER(**CONFIG,base_path=base_path)
            return rd
        
    match answers["mode"]:
        
        case "speak":
            rd = get_reader()
            text = questionary.text("text to speak").ask()
            rd.Speak(text=text)

        case "save audio":
            rd = get_reader()
            text = questionary.text("text to save").ask()
            filename = questionary.text("filename to save to").ask()

            rd.save_audio(filename=filename,text=text)


        case "benchmark":
            rd = get_reader()
            start = time.time()
            rd.save_audio(text="""
O Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise, but admirably balanced mind. He was, I take it, the most perfect reasoning and observing machine that the world has seen; but, as a lover, he would have placed himself in a false position. He never spoke of the softer passions, save with a gibe and a sneer. They were admirable things for the observer—excellent for drawing the veil from men’s motives and actions. But for the trained reasoner to admit such intrusions into his own delicate and finely adjusted temperament was to introduce a distracting factor which might throw a doubt upon all his mental results. Grit in a sensitive instrument, or a crack in one of his own high-power lenses, would not be more disturbing than a strong emotion in a nature such as his. And yet there was but one woman to him, and that woman was the late Irene Adler, of dubious and questionable memory.
""",filename="benchmark.wav")
            finished = time.time()
            print("Total Seconds: ",finished - start)

        case "remove-dedicated-venv":
            remove_venv(base_path=base_path,reader=READER)



        case "remove-current-venv":
            if sys.prefix != sys.base_prefix:
                shutil.rmtree(os.path.join(base_path,sys.prefix))

        case "install-in-dedicated-venv":
            make_dedicated_venv(base_path=base_path,reader=READER)

        case "install-in-current-venv":
            subprocess.run([sys.executable,"-m","pip","install","-r",READER.requirements])




@click.option("--ignore_venv",default=False,is_flag=True)
@click.command()
def main(ignore_venv):
        reader(ignore_venv)


if __name__ == '__main__':
    main()