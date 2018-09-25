import csv
import gzip
import os
import re
import urllib
from urllib.parse import urlparse

# DO NOT IMPORT NLTK ANYWHERE THAT USES MULTIPROCESSING! https://github.com/nltk/nltk/issues/947
# import nltk
from xml import etree

from bs4 import BeautifulSoup
from langdetect import detect
from src import util

# from src.features.HTML_sentence_tokenizer import HTMLSentenceTokenizer

raw_path = os.environ["DATA_PATH"] + "/raw/articles/"
sentences_path = os.environ["DATA_PATH"] + "/interim/sentences/"
sentences_english_path = os.environ["DATA_PATH"] + "/interim/sentences_english/"
tokens_path = os.environ["DATA_PATH"] + "/processed/tokens/"
processed_path = os.environ["DATA_PATH"] + "/processed/sentences/"

if not os.path.exists(raw_path):
    os.makedirs(raw_path)


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


def crawl(url):
    """
    Does not execute Javascript which is faster and yields more
    video_urls per unit of time, and since there are unlimited URL's it makes more sense this way.
    :param url:
    :return: BeautifulSoup of the page source
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla'})
    page_source = urllib.request.urlopen(req).read()
    return BeautifulSoup(page_source, features="lxml")


# These are used for a preliminary check. They do not yet guarantee that the src is acutally an embedded video that can be downloaded.
# That is done afterwards, when processing the data.
FB_VIDEO_IDENTIFIER = "www.facebook.com/plugins/video.php"
YT_VIDEO_IDENTIFIER = "www.youtube.com/embed"
TWITTER_IDENTIFIER_REGEX = r'twitter.com/[a-zA-Z0-9_]{1,15}/status'  # TODO cite source for this


def get_video_sources_bs(soup):
    """
    finds video iframes and gets their src attributes from a beatifulsoup object.
    This is purposefully broad, it can easily be filtered for invalid URLs etc. later, but crawling again is expensive.
    Plus the database doesn't take up much space.
    :param soup:
    :return:
    """
    iframes = soup.findAll("iframe")
    for iframe in iframes:
        if iframe.has_attr("src"):
            src = iframe['src']
            # Only youtube videos for now, but might include other sources at some point.
            if YT_VIDEO_IDENTIFIER in src:
                yield "youtube", src
            elif FB_VIDEO_IDENTIFIER in src:
                yield "facebook", src

    # Tweets are embedded blockquotes with class "twitter-tweet"
    blockquotes = soup.findAll("blockquote", "twitter-tweet")
    for blockquote in blockquotes:
        links = blockquote.findAll("a")
        if len(links) >= 1:
            link = links[-1]
            # The last link is the link to the tweet.
            if link.has_attr("href"):
                href = link["href"]
                if re.search(TWITTER_IDENTIFIER_REGEX, href):
                    yield "twitter", href


def get_video_sources_etree(etree):
    """
    finds video iframes and gets their src attributes from an etree.
    This is purposefully broad, it can easily be filtered for invalid URLs etc. later, but crawling again is expensive.
    Plus the database doesn't take up much space.
    :param etree:
    :return:
    """

    element_iterator = etree.iter()
    for element in element_iterator:
        if element.tag == "iframe":
            if "src" in element.attrib:
                if YT_VIDEO_IDENTIFIER in element.attrib["src"]:
                    yield "youtube", element.attrib["src"]
                elif FB_VIDEO_IDENTIFIER in element.attrib["src"]:
                    yield "facebook", element.attrib["src"]
        elif element.tag == "blockquote":
            for sub_element in element.iter():
                # next(element_iterator)
                if sub_element.tag == "a":
                    if "href" in sub_element.attrib:
                        if re.search(TWITTER_IDENTIFIER_REGEX, sub_element.attrib["href"]):
                            yield "twitter", sub_element.attrib["href"]


def get_path(url):
    return os.environ["DATA_PATH"] + "/raw/articles/%s" % urllib.parse.quote_plus(url)


def url_encode(url):
    """
    Makes a url safe to be used as a URL-parameter or filename.
    :param url:
    :return:
    """
    return urllib.parse.quote_plus(url)


def url_decode(filename):
    return urllib.parse.unquote_plus(filename)


def save(data, url):
    filename = url_encode(url)
    util.save_gzip_html(os.path.join(raw_path, filename), data)


def load(url):
    filename = urllib.parse.quote_plus(url)
    return util.load_gzip_html(os.path.join(raw_path, filename))


FILE_ENDING = ".gzip"


def get_article_filepath(url):
    """
    we ignore the fragment identifier as per https://tools.ietf.org/html/rfc3986 TODO quote
    :param url:
    :return:
    """
    parsed = urlparse(url)
    # Start with tld/domain/subdomain1/.../path1/path2/index.html?a=b#abc
    path = parsed.hostname.split(".")
    path.reverse()
    path += list(filter(None, parsed.path.split("/")))  # no empty strings
    if parsed.query:
        file_name = urllib.parse.quote_plus(parsed.query)
    else:
        file_name = path[-1]
        path = path[:-1]
    file_name += FILE_ENDING
    file_path = os.path.join(get_articles_path(), *path)
    return file_path, file_name


# TODO test cases


def get_articles_path():
    path = os.environ["DATA_PATH"] + "/raw/articles/"
    if not os.path.exists(path):
        os.makedirs(path)
    return path
