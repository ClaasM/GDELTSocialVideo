"""
Crawls all websites from "mentions" and saves which websites were successfully crawled and to which event id they belong.
Saves each found embedded youtube video id to the database.
Since crawling is I/O bound anyways, readability was prioritized over speed.
Anything else is nonsense in Python anyways.

Right now I've done multiple passes:
- One with the pool
- One without the pool, some sites don't handle


TODO extract
"""
from multiprocessing.dummy import Pool
from src.data.videos import video as video_helper

import psycopg2
import urllib3
from urllib3 import PoolManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from src.data.websites import website
from src import util, constants
from src.visualization.console import CrawlingProgress

''' Some intialization TODO use the separating comments from the BA '''

# Increasing pool size to 1000 gives a slight performance boost but requires increasing the open file limit
# https://www.ibm.com/support/knowledgecenter/en/SSRMWJ_6.0.0/com.ibm.isim.doc_6.0/trouble/cpt/cpt_ic_trouble_many_filesopen.htm
connection_pool = PoolManager(100, headers={'User-Agent': 'Mozilla'})
crawling_progress = CrawlingProgress(constants.GDELT_MENTIONS_LENGTH, update_every=100000)


def crawl_article(article):
    article_url, source_name = article
    videos = []
    try:
        # Sometimes, servers cannot handle connection pooling, so it is recommended to do a "second pass" without it.
        res = connection_pool.request('GET', article_url)
        if res.status >= 300:
            status = str(res.status)
        else:
            status = "Success"
            bs = BeautifulSoup(res.data, features="lxml")
            # find video iframes and get their src attributes
            videos = list(website.get_video_sources_bs(bs))
            if len(videos) > 0:
                # This website has videos in it, so it is saved
                website.save(bs.text, article_url)
    except Exception as e:
        # The website was not successfully crawled, it should be tried again
        status = str(e)

    return status, videos


def run():
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    # Only crawl articles that have not yet been crawled
    c.execute("SELECT source_url, source_name FROM articles WHERE crawling_status <> 'Success'")
    articles = c.fetchall()
    # parallel crawling and parsing to speed things up
    with Pool(4)  as pool:  # 16 seems to be around optimum
        for index, (status, videos) in enumerate(pool.imap(crawl_article, articles)):
            source_url = articles[index][0]
            # Update article crawling status
            c.execute("UPDATE articles SET crawling_status=%s WHERE source_url=%s", [status, source_url])
            # Save all the found videos to the database
            for platform, video_url in videos:
                if platform == "youtube":
                    video_id = video_helper.get_id_from_youtube_url(video_url)
                elif platform == "twitter":
                    video_id = video_helper.get_id_from_twitter_url(video_url)
                elif platform == "youtube":
                    video_id = video_helper.get_id_from_facebook_url(video_url)
                video_id = ""  # TODO remove this once the functions are implemented
                c.execute("""INSERT INTO videos (source_url, platform, video_url, video_id)
                              VALUES (%s, %s, %s, %s)""", [source_url, platform, video_url, video_id])
            c.commit()
        crawling_progress.inc(1)

    conn.commit()


if __name__ == "__main__":
    run()

    # TODO POPULATE THE SOURCES TABLE
