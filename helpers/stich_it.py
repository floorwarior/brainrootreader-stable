
def sort_by_name(filename):
    a, b  = filename.rsplit("_")
    b :str
    c = b.removesuffix(".wav")
    return int(c)


def stich_playlist_to_file(folder_name,book_name,ext):
    """converts the playlist into one singular file to use
    - folder_name: name of the folder where the pages.audio files are
    - book_name the new or the original name of the book
    - ext : example wav
    """
    from pydub import AudioSegment
    import glob 
    import os
    if not book_name:
        book_name = "unnamed_book"

    new_file_path = os.path.join(folder_name,f"{book_name}.{ext}")
    print(f"[ THIS IS WHERE WE SAVE THE FILE: {new_file_path}]")
    if os.path.exists(new_file_path):
        return False

    files = glob.glob(f"*.{ext}",root_dir=folder_name)


    files.sort(key = lambda x: sort_by_name(x))
    pages = [AudioSegment.from_file(file=os.path.join(folder_name,file),format=ext) for file in files]

    playlist = pages.pop(0)
    for page in pages:
        playlist = playlist + page

    playlist.export(os.path.join(folder_name,f"{book_name}.{ext}"),format=ext)
    print(f"[ SAVED AUDIO TO: {new_file_path}]")


