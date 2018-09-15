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


def load_gzip_html(path):
    with gzip.open(path, "rb") as file:
        return file.read().decode("utf-8")


def save_gzip_html(path, html):
    with gzip.open(path, "wb+") as file:
        file.write(html.encode("utf-8"))


def append_line(path, line):
    with gzip.open(path, "w+") as outfile:
        outfile.write(line + "\n")





def is_url(string):
    if validators.url(string):
        return True
    else:
        return False  # We just want boolean values, no ValidationFailure objects
