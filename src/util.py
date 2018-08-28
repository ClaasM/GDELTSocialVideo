import gzip
import pickle
import os


def to_plaintext(path, destination):
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

#data_path = "../data"
#file = 1078
#to_plaintext(data_path + ("/raw/articles/%d" % file),
#             data_path + ("/interim/unzipped/%d.html" % file))
