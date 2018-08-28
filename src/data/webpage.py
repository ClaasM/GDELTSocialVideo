import gzip
import os
import pickle
import urllib

from bs4 import BeautifulSoup
from langdetect import detect

from src.features.HTML_sentence_tokenizer import HTMLSentenceTokenizer

path = "data/GDELT_VGKG/articles"
raw_path = path + "/raw"
sentences_path = path + "/sentences"
sentences_english_path = path + "/sentences_english"
tokenized_path = path + "/tokens"


def download_and_save(row):
    """
    Queues a webpage for download if it does not exist
    :param id: Name of the file
    :param url: URL of the image
    :return:
    """
    index, (date, document_identifier, image_URL, raw_JSON) = row
    article_path = raw_path + "/" + str(date)
    if os.path.isfile(article_path):
        return "Already exists"
    else:
        try:
            # Download document
            req = urllib.request.Request(document_identifier, headers={'User-Agent': 'Mozilla'})
            doc = urllib.request.urlopen(req, timeout=5).read()

            with gzip.open(article_path, "wb+") as file:
                pickle.dump(doc, file)
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
        with gzip.open(file, "rb") as file:
            doc = pickle.load(file)

        bs_doc = BeautifulSoup(doc, features="lxml")

        # remove some tags that aren't rendered, including their content
        # From https://www.w3schools.com/tags/ref_byfunc.asp
        programming_tags = ['script', 'noscript', 'applet', 'embed', 'object', 'param']
        meta_tags = ['head', 'meta', 'base', 'basefont']
        other_tags = ['data', 'style', 'iframe']
        [x.extract() for x in bs_doc.findAll(programming_tags + meta_tags + other_tags)]

        sentences = HTMLSentenceTokenizer().feed(str(bs_doc))

        # Done preprocessing. Save tokens
        with gzip.open("%s/%s" % (sentences_path, filename), "wb+") as file:
            pickle.dump(sentences, file)
        return "Success"
    except Exception as e:
        return str(e)


def tokenize_and_save():
    """
    TODO
    :return:
    """
    pass
    # Keep only the remaining text (removing all tags etc.)
    # text = bs_doc.get_text()  # re.sub('<[^<]+?>', '', str(doc))[:100]

    # Tokenize the text
    # tokens = nltk.word_tokenize(text)

    # Keep only tokens that are words and more than a letter
    # alpha_tokens = [token for token in tokens if token.isalpha() and len(token) > 1]

    # Keep only tokens that are either all caps or no caps or start with a capital letter
    # pattern = re.compile("(^[A-Z]?[a-z]+$)|(^[A-Z]+$)")
    # word_tokens = [token for token in alpha_tokens if pattern.match(token)]


def save_if_english(file):
    """
    :param doc:
    :return:
    """
    filename = file.split("/")[-1]
    try:
        with gzip.open(file, "rb") as file:
            sentences_array = pickle.load(file)
        language = detect(' '.join(sentences_array))
        if language == 'en':
            with gzip.open("%s/%s" % (sentences_english_path, filename), "wb+") as file:
                pickle.dump(sentences_array, file)
        return language
    except Exception as e:
        return str(e)
