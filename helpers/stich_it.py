
def sort_by_name(filename):
    a, b  = filename.rsplit("_")
    b :str
    c = b.removesuffix(".wav")
    return int(c)


def stich_playlist_to_file(folder_name,book_name,ext):
    from pydub import AudioSegment
    import glob 
    import os


    """takes the pages and makes it into one file"""
    files = glob.glob(f"*.{ext}",root_dir=folder_name)
    files.sort(key = lambda x: sort_by_name(x))

    pages = [AudioSegment.from_file(file=os.path.join(folder_name,file),format=ext) for file in files]

    playlist = pages.pop(0)
    for page in pages:
        playlist = playlist + page

    playlist.export(book_name,format=ext)


