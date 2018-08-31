"""
Crawls all websites from "mentions" and saves which websites were successfully crawled and to which event id they belong.
Saves each found embedded youtube video id to the database.
Since crawling is I/O bound anyways, readability was prioritized over speed.
Anything else is nonsense in Python anyways.
"""
import glob
import os
import pandas as pd
from multiprocessing.dummy import Pool as DummyPool
from src.data.sqlite.sqlite_helper import SQLiteHelper
from src.data.websites import website
from src import util

# Data availability is not a problem, so I'm only using articles that are 100% confident to be about the event
# This increases relevance of the videos.
CONFIDENCE_THRESHOLD = 100


def crawl_urls(file):
    """
    Crawls all urls in a mentions-file.
    This is done for each 15-minute file.
    :param file:
    :return:
    """
    print("Starting file %s" % file)
    # We only need a couple of columns
    mentions = pd.read_csv(file, compression='zip', header=None,
                           names=["GlobalEventID", "MentionIdentifier", "Confidence"],
                           delimiter="\t",
                           usecols=[0, 5, 11])
    # SQLite connections have to be created in the thread they are used.
    sqlite_helper = SQLiteHelper()
    for index, (global_event_id, mention_identifier, confidence) in mentions.iterrows():
        if util.is_url(mention_identifier) and confidence >= CONFIDENCE_THRESHOLD:
            # Mentions are not always from a website, so MentionIdentifier is not always a URL. Those that aren't are skipped.
            # TODO pie chart of how many are URLS (split by MentionSourceName)
            # Also, mentions of an event with too little confidence are skipped.
            if sqlite_helper.is_crawled(mention_identifier):
                # This website has already been successfully crawled.
                # All the videos from that website, are now also associated with this Event ID.
                print("Already successfully crawled: %s" % mention_identifier)
                if sqlite_helper.has_videos(mention_identifier):
                    # The website has videos on it, so this mention of this event needs to saved with a link to the website.
                    # The video ids from this website were already saved when the website was first crawled.
                    sqlite_helper.save_mention(global_event_id, mention_identifier)
                    print("Already saved videos: %s" % mention_identifier)
            else:
                # crawl the website.
                # Whatever happens, the results is saved. This is useful information, because re-crawling is expensive.
                try:
                    bs = website.crawl(mention_identifier)
                    # find video iframes and get their src attributes
                    video_urls = list(website.get_iframe_video_sources(bs))
                    if len(video_urls) > 0:
                        # This website has videos in it
                        sqlite_helper.save_mention(global_event_id, mention_identifier)
                        for video_url in video_urls:
                            sqlite_helper.save_found_video_url(mention_identifier, video_url)
                            print("Found video saved: %s %s" % (video_url, mention_identifier))
                    # Either way, the website has been successfully crawled and processed, and doesn't need to be crawled again.
                    sqlite_helper.save_crawled(mention_identifier, "Success")
                    print("Saved as crawled: %s" % mention_identifier)
                except Exception as e:
                    # The website was not successfully crawled, it should be tried again
                    print(e)
                    sqlite_helper.save_crawled(mention_identifier, str(e))


# We create a Pool (of Threads, not processes, since, again, this task is I/O-bound anyways)
mentions_path = os.environ["DATA_PATH"] + "/external/GDELT/mentions/"
files = glob.glob(mentions_path + "[0-9]*.mentions.csv.zip")
pool = DummyPool(8)

count = 0
for _ in pool.imap(crawl_urls, files):
    count += 1
    if count % 1 == 0:
        print(count)
pool.close()
pool.join()
