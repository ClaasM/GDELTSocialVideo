# crawl any websites that dont contain </html>
import re
from multiprocessing.pool import Pool

import htmlmin
import psycopg2
import sys

import requests

from src.data.videos import video as video_helper
from src.data.websites import website as website_helper
from src.visualization.console import CrawlingProgress

minifier = htmlmin.Minifier(remove_comments=True, remove_all_empty_space=True, reduce_boolean_attributes=True,
                            remove_empty_space=True)

def crawl_article(article):
    url, = article
    try:
        res = requests.get(url, headers={"user-agent": "Mozilla"})
        if res.status_code >= 300:
            print(res.status_code)
        else:
            website_helper.save(minifier.minify(res.text), url)
    except Exception as e:
        # The website was not successfully crawled, it should be tried again
        print(e)
        return str(e)

    return "Success"

def run():
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")

    c = conn.cursor()
    c.execute("SELECT DISTINCT source_url from article_videos")
    articles = c.fetchall()

    crawling_progress = CrawlingProgress(len(articles), update_every=10000)

    # parallel crawling and parsing to speed things up
    with Pool(32)  as pool:  # 16 seems to be around optimum
        for _ in pool.imap_unordered(crawl_article, articles, chunksize=100):
            crawling_progress.inc(1)


if __name__ == "__main__":
    run()