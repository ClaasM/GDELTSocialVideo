"""
Crawls all the websites that contain any downloaded video and saves the extracted article text.
TODO document (some can be copied over from the mentions crawler)
"""
import glob
import os
from multiprocessing.pool import Pool

import psycopg2
from urllib3 import PoolManager

from src.data.websites import website
from src.visualization.console import CrawlingProgress

import urllib3

urllib3.disable_warnings()

connection_pool = PoolManager(100)
crawling_progress = CrawlingProgress(0, update_every=1000)


def crawl_url(url):
    if not os.path.exists(website.get_path(url)):
        try:
            # Sometimes, servers cannot handle connection pooling, so it is recommended to do a "second pass" without it.
            res = connection_pool.request('GET', url, headers={'User-Agent': 'Mozilla'})
            if res.status >= 300:
                print(res.status)
            else:
                print(str(res.status)  + url)
                pass
                # TODO extract the article from res.data using boilerpipe
        except Exception as e:
            # The website was not successfully crawled, it should be tried again
            print(e)
    crawling_progress.inc(by=1)


def run():
    platform = "youtube"
    resolution = "lowest_res"

    # TODO maybe do this in the videos module
    videos_path = os.environ["DATA_PATH"] + "/raw/GDELT/videos/%s/%s/random1000/" % (platform, resolution)
    video_files = glob.glob(os.path.join(videos_path, "*.mp4"))  # TODO replace all with path.join

    conn = psycopg2.connect(database="thesis", user="postgres")
    c = conn.cursor()

    urls_to_crawl = set()
    for video_file in video_files:
        video_id = video_file.split("/")[-1].split(".")[0]
        c.execute("SELECT (website_url) from found_videos WHERE platform='%s' AND video_url LIKE '%%%s%%'" \
                  % (platform, video_id))
        urls_to_crawl.add(c.fetchone()[0])

    print(len(urls_to_crawl))
    crawling_progress.set_total_count(len(urls_to_crawl))
    pool = Pool(4)
    count = 0
    for _ in pool.imap_unordered(crawl_url, urls_to_crawl):
        count += 1
    pool.close()
    pool.join()


if __name__ == "__main__":
    run()
