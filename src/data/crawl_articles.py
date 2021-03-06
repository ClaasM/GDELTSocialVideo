"""
Crawls all articles and saves which articles were successfully crawled.
Saves each found embedded youtube or facebook video and twitter tweets to the database.
Since crawling is I/O bound anyways, readability was prioritized over speed.
Anything else is nonsense in Python anyways.
"""

from multiprocessing import Pool

import psycopg2
import requests
import urllib3
import htmlmin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from src.data.websites import website as website_helper
from src.visualization.console import StatusVisualization

''' Some intialization '''

minifier = htmlmin.Minifier(remove_comments=True, remove_all_empty_space=True, reduce_boolean_attributes=True,
                            remove_empty_space=True)


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
            videos = list(website_helper.get_video_sources_bs(bs))
            if len(videos) > 0:
                # This website has videos in it, so it is saved
                website_helper.save(minifier.minify(res.text), article_url)
    except Exception as e:
        # The website was not successfully crawled, it should be tried again
        status = str(e)
        # print(status)

    return index, status, videos


def run(db, user):
    conn = psycopg2.connect(database=db, user=user)
    c = conn.cursor()
    # Only crawl articles that have not yet been crawled
    c.execute("SELECT source_url, source_name FROM articles WHERE crawling_status<>'Success'")
    articles = c.fetchall()
    crawling_progress = StatusVisualization(len(articles), update_every=10000)
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
                c.execute(
                    "INSERT INTO sources (source_name)  VALUES (%s) ON CONFLICT (source_name) DO UPDATE SET article_count = sources.article_count + 1",
                    [source_name])
                # ...Save all the found videos to the database
                for platform, video_id in videos:
                    # Insert it into the videos table s.t. it contains all videos in the end
                    c.execute("INSERT INTO videos (platform, id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                              [platform, video_id])
                    c.execute("""INSERT INTO article_videos (source_url, source_name, platform, video_id)
                                  VALUES (%s, %s, %s, %s)""", [source_url, source_name, platform, video_id])
            conn.commit()
            crawling_progress.inc(1)


import argparse

parser = argparse.ArgumentParser(description='Crawls articles in the articles table of a specified database.')

parser.add_argument('--db', help='Database containing the article URLs. Default: "gdelt_social_video"', type=str,
                    default="gdelt_social_video")
parser.add_argument('--user', nargs='+', help='Username for the database. No password. Default: "postgres"', type=str,
                    default="postgres")

args = parser.parse_args()

if __name__ == "__main__":
    try:
        run(args.db, args.user)
    except KeyboardInterrupt:
        print("Interrupted by user. To resume, run again.")
        pass
