from helpers.book_conversion_from_images import ConvertFromImages


if __name__ == "__main__":
    res = ConvertFromImages.test_one(tesseractlocation="r/afla/Desktop",filename="never been a thing",lang="eng")
    print(res)

