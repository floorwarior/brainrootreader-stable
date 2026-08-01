from helpers.book_conversion_from_txt import ConvertFromTxt
from helpers.get_root import getroot

import os

root = getroot()
cvrt = ConvertFromTxt(
    basepath=root,
    txtfilename=os.path.join(root,"tests/testfiles/test.txt"),
    chunksize=15
)

cvrt.convert_txt_file()