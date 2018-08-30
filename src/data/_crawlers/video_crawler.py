import glob
import os
import urllib
from multiprocessing import Pool

import pandas as pd
from bs4 import BeautifulSoup
from pytube import YouTube
from src import util

raw_video_path = os.environ["DATA_PATH"] + "/raw/GDELT/videos/"
raw_article_path = os.environ["DATA_PATH"] + "/raw/GDELT/articles/"
GDELT_path = os.environ["DATA_PATH"] + "/external/GDELT/"

"""
Each Event can have multiple
"""

import sqlite3

conn = sqlite3.connect('GDELT.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS videos
             (GLOBALEVENTID integer, url text, video_id text)''')


def website_crawled_successfully(url):
    """
    Checks if url has already been crawled succesfully.
    :param url:
    :return:
    """
    return c.execute('''SELECT EXISTS(SELECT 1 FROM crawled_websites WHERE url=\'%s\')''' % url).fetchall()

def


def crawl_all(file):
    print("Starting file %s" % file)
    # driver = webdriver.Chrome()

    df = pd.read_csv(file, compression='zip', header=None, names=util.GDELT_HEADER, delimiter="\t", usecols=[0, 60])
    for index, row in df.iterrows():
        _id, url = str(row[0]), row[-1]
        if website_crawled_successfully(url):
            # This website has already been successfully crawled.
            # All the videos from that website, are now also associated with this Event ID.
            save_videos()
        else:
            #print("Crawling %s" % url)
            try:
                # Rendering JS all the time is a little too intense, so the we just disregard it.
                # driver.get(url)
                # page_source = driver.page_source
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla'})
                page_source = urllib.request.urlopen(req).read()
                soup = BeautifulSoup(page_source, features="lxml")
                iframes = soup.findAll("iframe")
                for iframe in iframes:
                    if iframe.has_attr("src"):
                        src = iframe['src']
                        if "youtube.com" in src:
                            print("Found yt iframe: %s" % src, end=' ')
                            filename = src.split("/")[-1].split("?")[0]
                            if(os.path.exists(raw_video_path + filename + ".mp4")):
                                print("Already exists! %s" % filename)
                                YouTube(src) \
                                    .streams \
                                    .filter(progressive=True, file_extension='mp4') \
                                    .order_by('resolution') \
                                    .asc() \
                                    .first() \
                                    .download(output_path=raw_video_path, filename=filename)
                            # Save the link between that video and that article
                            # TODO continue here
                            print("Success!")
                # the webpage is only saved as crawled if every video and the website itself were successfully crawled.
                # otherwise it will be crawled again if improvements are made to the crawler
                # TODO
            except Exception as e:
                print(str(e))


files = glob.glob(os.environ["DATA_PATH"] + "/external/GDELT/[0-9]*.export.CSV.zip")
pool = Pool(8)
results = list()

for result in pool.imap(crawl_all, files):
    results.append(result)
    if len(results) % 10 == 0:
        print(len(results))
pool.close()
pool.join()
