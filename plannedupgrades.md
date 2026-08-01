# List of things that are planned to appear:
| function | planned release | status |
| :----- | ----: | :--:|
| flash cards: i want this app to be study friendly | ~~2025 nov~~; 2026 aug | done | 
| better accesibility support, already have some items with area support, you can use the r key to read any such item when navigating  | 2025 oct->dec | in progress | 
| more flexible dependency management: gonna add a page that checks if the user has the proper items installed [1]  | ~~2025 oct~~  | canceled | 
| benchmark: testing your pc-s strenght on a small text set to see how fast it can generate text [2] | ~~2025 nov~~ | canceled |
| notes: adding notes for any ~~sentence~~ page | 2025 oct | done |
| .brr file type: includes notes,cards, imgs, text of the document edit1: will probably be rolled back | 2025 nov  | done |
| kokoro reader  | 2025 oct| added | 
| translating the ui | 2025 nov| canceled|
| brainrootreader-light: a lighter verion that only includes PiperReader | 2025 dec| canceled | 
| full ui rewrite in tailwind i am not very happy with the current ui | 2026 jul | done |
| themeing | 2026 aug-sep | new theme is gray-green, might add more later |
| command line interface | 2026 aug | in progress | 
| engine builder: builds a pinned engine from a :readerclass: and it's arguments| 2026 sept | todo |
| >> selenium testing pipeline: currently i have to do manual testing which is hell | 2026 aug-sept | todo, next in queue |
| more readers: will probably add Kitten-tts | 2026 aug | todo |
| ReadBook: complete rewrite most likely with composition, there is a lot of dead code there and the running code is not good quality | 2026 oct | todo |


* [1]: ended up adding a system instead that installs readers into dedicated venv's, this blocks a lot of the early problems i had where some project has the same packages with conflicting versions, thanks to the subprocess approach these are not running in their own venv, so there is no conflict, i also added more warnings for missig packages, these checks will probably will move to the first part of background.py to make failing faster.

*[2]: there is a tiny benchmark if you are using the cli with `python.exe -m tools.cli` but this is not very stable/reliable currently. If you are trying to figure out what can you run reading the README's : What backend to pick? section should be greater help.
