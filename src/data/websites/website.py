import csv
import gzip
import os
import re
import urllib

import nltk
from bs4 import BeautifulSoup
from langdetect import detect
from src import util
from src.features.HTML_sentence_tokenizer import HTMLSentenceTokenizer

raw_path = os.environ["DATA_PATH"] + "/raw/articles/"
sentences_path = os.environ["DATA_PATH"] + "/interim/sentences/"
sentences_english_path = os.environ["DATA_PATH"] + "/interim/sentences_english/"
tokens_path = os.environ["DATA_PATH"] + "/processed/tokens/"
processed_path = os.environ["DATA_PATH"] + "/processed/sentences/"


def download_and_save(row):
    """
    Queues a webpage for download if it does not exist
    :param id: Name of the file
    :param url: URL of the image
    :return:
    """
    index, (date, document_identifier, image_URL, raw_JSON) = row
    article_path = raw_path + "/" + str(index)
    if os.path.isfile(article_path):
        return "Already exists"
    else:
        try:
            # Download and save document
            req = urllib.request.Request(document_identifier, headers={'User-Agent': 'Mozilla'})
            doc = urllib.request.urlopen(req).read()
            util.save_gzip_pickle(article_path, doc)
            return "Success"
        except Exception as e:
            return str(e)


def extract_sentences_and_save(file):
    """
    Removes anything unnecessary from an HTML Document. Keeps an array of sentences.
    :param doc:
    :return:
    """
    filename = file.split('/')[-1]

    try:
        doc = util.load_gzip_pickle(file)

        bs_doc = BeautifulSoup(doc, features="lxml")

        # remove some tags that aren't rendered, including their content
        # From https://www.w3schools.com/tags/ref_byfunc.asp
        programming_tags = ['script', 'noscript', 'applet', 'embed', 'object', 'param']
        meta_tags = ['head', 'meta', 'base', 'basefont']
        other_tags = ['data', 'style', 'iframe']
        [x.extract() for x in bs_doc.findAll(programming_tags + meta_tags + other_tags)]

        sentences = HTMLSentenceTokenizer().feed(str(bs_doc))

        # Done preprocessing. Save tokens
        util.save_gzip_pickle("%s/%s" % (sentences_path, filename), sentences)
        return "Success"
    except Exception as e:
        return str(e)


def tokenize_and_save(file):
    """
    TODO
    :return:
    """
    filename = file.split('/')[-1]

    try:
        sentences = util.load_gzip_pickle(file)

        text = ' '.join(sentences)

        # Tokenize the text
        tokens = nltk.word_tokenize(text)

        # Keep only tokens that are words and more than a letter
        alpha_tokens = [token for token in tokens if token.isalpha() and len(token) > 1]

        # Keep only tokens that are either all caps or no caps or start with a capital letter
        pattern = re.compile("(^[A-Z]?[a-z]+$)|(^[A-Z]+$)")
        word_tokens = [token for token in alpha_tokens if pattern.match(token)]

        # Done preprocessing. Save tokens
        util.save_gzip_pickle("%s/%s" % (tokens_path, filename), word_tokens)

        return "Success"
    except Exception as e:
        return str(e)


def save_if_english(file):
    """
    :param doc:
    :return:
    """
    filename = file.split("/")[-1]
    try:
        sentences_array = util.load_gzip_pickle(file)
        language = detect(' '.join(sentences_array))
        if language == 'en':
            util.save_gzip_pickle("%s/%s" % (sentences_english_path, filename), sentences_array)
        return language
    except Exception as e:
        return str(e)


def get_row_by_date(date):
    with gzip.open(os.environ["DATA_PATH"] + '/external/vgkg-20160427-part1.csv.gz', "rt") as gzipfile:
        reader = csv.reader(gzipfile)
        DATE = None
        index = -1
        while DATE != str(date):
            index += 1
            (DATE, DocumentIdentifier, ImageURL, RawJSON) = next(reader)
        return index, (DATE, DocumentIdentifier, ImageURL, RawJSON)


def get_row_by_index(index):
    index = int(index)
    with gzip.open(os.environ["DATA_PATH"] + '/external/vgkg-20160427-part1.csv.gz', "rt") as gzipfile:
        reader = csv.reader(gzipfile)
        next(reader)  # Skip headers
        row = next(reader)
        curr_index = 0
        while curr_index != index:
            curr_index += 1
            row = next(reader)
        return row


word_limit_lower = 4
word_limit_upper = 200
sentence_limit_lower = 20
sentence_upper_limit = 200


def save_if_passes_filter(file):
    """
    Loads the file and checks if it passes the filter. If so, its saved to the 'processed' directory
    TODO maybe add check for casing?
    :param file:
    :return:
    """
    filename = file.split("/")[-1]
    try:
        sentences_array = util.load_gzip_pickle(file)
        sentences_array = [sentence for sentence in sentences_array if
                           word_limit_lower < len(sentence.split(" ")) < word_limit_upper]

        if sentence_limit_lower < len(sentences_array) < sentence_upper_limit:
            util.save_gzip_pickle("%s/%s" % (processed_path, filename), sentences_array)
            return True
        return False
    except Exception as e:
        return str(e)

def get_language_header(row):
    index, (date, document_identifier, image_URL, raw_JSON) = row
    try:
        req = urllib.request.Request(document_identifier, headers={'User-Agent': 'Mozilla'})
        res = urllib.request.urlopen(req)
        return res.headers["Content-Language"]
    except Exception as e:
        return str(e)
