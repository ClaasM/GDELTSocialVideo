"""
Crawls all websites from "mentions" and saves which websites were successfully crawled and to which event id they belong.
Saves each found embedded youtube video id to the database.
Since crawling is I/O bound anyways, readability was prioritized over speed.
Anything else is nonsense in Python anyways.

Right now I've done multiple passes:
- One with the pool
- One without the pool, some sites don't handle
"""
import csv
import glob
import io
import os
import urllib
import zipfile
from multiprocessing import Pool

import psycopg2
import urllib3
from urllib3 import PoolManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from bs4 import BeautifulSoup

from src.data.postgres.postgres_helper import PostgresHelper
from src.data.websites import website
from src import util, constants
from src.visualization.console import CrawlingProgress

''' Some intialization TODO use the separating comments from the BA '''

# Data availability is not a problem, so I'm only using articles that are 100% confident to be about the event
# This increases relevance of the videos.
CONFIDENCE_THRESHOLD = 100
# Increasing pool size to 1000 gives a slight performance boost but requires increasing the open file limit
# https://www.ibm.com/support/knowledgecenter/en/SSRMWJ_6.0.0/com.ibm.isim.doc_6.0/trouble/cpt/cpt_ic_trouble_many_filesopen.htm
# Sometimes, servers cannot handle connection pooling, so it is recommended to do a "second pass" without it.
# connection_pool = PoolManager(100)
crawling_progress = CrawlingProgress(constants.GDELT_MENTIONS_LENGTH, update_every=100000)


def crawl_urls(filepath):
    """
    Crawls all urls in a mentions-file.
    This is done for each 15-minute file.
    :param file:
    :return:
    """
    # reading manually instead of with pandas to relieve some memory,
    # and also because pandas seems to sometimes forget closing files
    archive = zipfile.ZipFile(filepath)
    file = archive.open(archive.namelist()[0])
    reader = csv.reader(io.TextIOWrapper(file), delimiter='\t')

    # SQLite connections have to be created in the thread they are used.
    sqlite_helper = PostgresHelper()
    index = 0
    for row in reader:
        global_event_id, mention_identifier, confidence = row[0], row[5], int(row[11])
        # Report progress only every 100 mentions
        if index % 100 == 0 and index != 0:
            crawling_progress.inc(by=100)
        if util.is_url(mention_identifier) and confidence >= CONFIDENCE_THRESHOLD:
            # Mentions are not always from a website, so MentionIdentifier is not always a URL. Those that aren't are skipped.
            # TODO pie chart of how many are URLS (split by MentionSourceName)
            # Also, mentions of an event with too little confidence are skipped.
            if sqlite_helper.is_crawled(mention_identifier):
                # This website has already been successfully crawled.
                # All the videos from that website, are now also associated with this Event ID.
                # print("Already successfully crawled: %s" % mention_identifier)
                if sqlite_helper.has_videos(mention_identifier):
                    # The website has videos on it, so this mention of this event needs to saved with a link to the website.
                    # The video ids from this website were already saved when the website was first crawled.
                    sqlite_helper.save_mention_with_video(global_event_id, mention_identifier)
                    # print("Already saved videos: %s" % mention_identifier)
            else:
                # crawl the website.
                # Whatever happens, the results is saved. This is useful information, because re-crawling is expensive.
                try:
                    # Sometimes, servers cannot handle connection pooling, so it is recommended to do a "second pass" without it.
                    # res = connection_pool.request('GET', mention_identifier, headers={'User-Agent': 'Mozilla'})

                    req =  urllib.request.Request(mention_identifier, headers={'User-Agent': 'Mozilla'})
                    res = urllib.request.urlopen(req)
                    res.data = res.read()

                    if res.status >= 300:
                        # The website was not successfully crawled, it should be tried again
                        # print(res.status)
                        sqlite_helper.save_crawled(mention_identifier, str(res.status))
                    else:
                        bs = BeautifulSoup(res.data, features="lxml")
                        video_urls = list(website.get_video_sources_bs(bs))
                        # et = etree.fromstring(res.data)
                        # video_urls = list(website.get_video_sources_etree(et))
                        # find video iframes and get their src attributes
                        if len(video_urls) > 0:
                            # This website has videos in it
                            sqlite_helper.save_mention_with_video(global_event_id, mention_identifier)
                            for platform, video_url in video_urls:
                                sqlite_helper.save_found_video_url(mention_identifier, platform, video_url)
                                # print("Found video saved: %s %s" % (video_url, mention_identifier))
                        # Either way, the website has been successfully crawled and processed, and doesn't need to be crawled again.
                        sqlite_helper.save_crawled(mention_identifier)
                        # print("Saved as crawled: %s" % mention_identifier)
                except Exception as e:
                    # The website was not successfully crawled, it should be tried again
                    print(e)
                    sqlite_helper.save_crawled(mention_identifier, str(e))
        index += 1
    # report the remaining, unreported read lines and
    crawling_progress.inc(by=index % 100)
    file.close()
    archive.close()
    sqlite_helper.disconnect()


def run():
    # We create a Pool (of Threads, not processes, since, again, this task is I/O-bound anyways)
    mentions_path = os.environ["DATA_PATH"] + "/external/mentions/"
    files = glob.glob(mentions_path + "[0-9]*.mentions.csv.zip")
    pool = Pool(32)  # 16 seems to be around optimum

    count = 0
    for _ in pool.imap_unordered(crawl_urls, files):
        count += 1
    pool.close()
    pool.join()


if __name__ == "__main__":
    run()
