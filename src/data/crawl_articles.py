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
from multiprocessing import Pool

import psycopg2
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from src.data.websites import website
from src.visualization.console import CrawlingProgress

''' Some intialization TODO use the separating comments from the BA '''


def crawl_article(article):
    index, (article_url, source_name) = article
    videos = []
    try:
        res = requests.get(article_url, headers={"user-agent": "Mozilla"})
        if res.status_code >= 300:
            status = str(res.status_code)
        else:
            status = "Success"
            bs = BeautifulSoup(res.text, features="lxml")
            # find video iframes and get their src attributes
            videos = list(website.get_video_sources_bs(bs))
            if len(videos) > 0:
                # This website has videos in it, so it is saved
                website.save(bs.text, article_url)
    except Exception as e:
        # The website was not successfully crawled, it should be tried again
        status = str(e)

    return index, status, videos


def run():
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    # Only crawl articles that have not yet been crawled
    c.execute("SELECT source_url, source_name FROM articles WHERE crawling_status <> 'Success'")
    articles = c.fetchall()
    crawling_progress = CrawlingProgress(len(articles), update_every=10000)
    # parallel crawling and parsing to speed things up
    with Pool(32)  as pool:  # 16 seems to be around optimum
        for (index, status, videos) in pool.imap_unordered(crawl_article, enumerate(articles), chunksize=100):
            source_url = articles[index][0]
            source_name = articles[index][1]
            # Update article crawling status
            c.execute("UPDATE articles SET crawling_status=%s WHERE source_url=%s", [status, source_url])
            # If the article has been successfully crawled...
            if status == 'Success':
                # ...Update the article count in the sources table
                c.execute("INSERT INTO sources (source_name)  VALUES (%s) ON CONFLICT (source_name) DO UPDATE SET article_count = sources.article_count + 1", [source_name])
                # ...Save all the found videos to the database
                for platform, video_url in videos:
                    c.execute("""INSERT INTO videos (source_url, source_name, platform, video_url)
                                  VALUES (%s, %s, %s, %s)""", [source_url, source_name, platform, video_url])
            conn.commit()
            crawling_progress.inc(1)


if __name__ == "__main__":
    run()
