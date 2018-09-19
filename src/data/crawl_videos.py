import glob
import os
from multiprocessing import Pool
from random import shuffle

import psycopg2
import time
from pytube import YouTube
from pytube.exceptions import RegexMatchError
import logging
from src.data.videos import video as video_helper
from src.visualization.console import SyncedCrawlingProgress

raw_video_path = os.environ["DATA_PATH"] + "/raw/videos/%s/%s/random1000" % (platform, resolution)
os.makedirs(raw_video_path, exist_ok=True)

logging.basicConfig(filename=os.path.join(raw_video_path, '%d.log' % time.time()), level=logging.DEBUG)


def download_yt_video(video):



def run():
    # We create a Pool (of Threads, not processes, since, again, this task is I/O-bound anyways)
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    c.execute(
        """SELECT found_videos.video_url FROM (found_videos
            LEFT JOIN hosts ON hosts.hostname=found_videos.hostname)
            WHERE hosts.youtube_relevant=TRUE AND platform=%s""", [platform])

    videos = c.fetchall()
    shuffle(videos)
    videos = videos[:1000]
    pool = Pool(4)
    crawling_progress = SyncedCrawlingProgress(len(videos), update_every=10)
    for _ in pool.imap_unordered(download_yt_video, videos):
        crawling_progress.inc(by=1)
    pool.close()
    pool.join()


if __name__ == "__main__":
    run()
