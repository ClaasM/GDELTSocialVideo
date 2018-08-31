import gzip
import pickle
import validators


def gzip_to_plaintext(path, destination):
    """
    Saves a file unzipped and unpickled, for manual inspection
    :param path: input file path
    :param destination: where the plain text file will be saved
    :return: None
    """
    with gzip.open(path, "rb") as infile:
        doc = pickle.load(infile)
        with open(destination, "wb+") as outfile:
            outfile.write(doc)
            outfile.close()


def load_gzip_pickle(path):
    """
    Loads a gzipped pickle
    :param path: file path
    :return: The python object
    """
    with gzip.open(path, "rb") as infile:
        return pickle.load(infile)


def save_gzip_pickle(path, object):
    """
    Saves python object as a gzipped pickle
    :param path: file path
    :return: The python object
    """
    with gzip.open(path, "wb+") as file:
        pickle.dump(object, file)


def append_line(path, line):
    with gzip.open(path, "w+") as outfile:
        outfile.write(line + "\n")


def get_filename_from_url(url):
    return url.split("/")[-1]

def is_url(string):
    if validators.url(string):
        return True
    else:
        return False # We just want boolean values, no ValidationFailure objects

def extract_video_id(url):
    """
    Not failsafe (its not supposed to be)
    :param url:
    :return:
    """
    # https://www.youtube.com/embed/ZdLMtnNkHvQ?rel=0
    #//www.youtube.com/embed/?wmode=opaque&hd=1&autoplay=0&showinfo=0&controls=0&rel=0
    return url.split('/')[-1].split('?')[0]
