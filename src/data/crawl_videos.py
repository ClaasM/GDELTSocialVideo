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

length_cuttoff = 3600  # Nothing longer than an hour
size_cutoff = 10000000000  # Nothing above 10 GB
platform = "youtube"
resolution = "lowest_res"
raw_video_path = os.environ["DATA_PATH"] + "/raw/videos/%s/%s/random1000" % (platform, resolution)
os.makedirs(raw_video_path, exist_ok=True)

logging.basicConfig(filename=os.path.join(raw_video_path, '%d.log' % time.time()), level=logging.DEBUG)


def download_yt_video(video):
    url = video[0]
    try:
        # Extract the video_id
        video_id = video_helper.get_id_from_youtube_url(url)
        # If it's already downloaded, do nothing
        if glob.glob(os.path.join(raw_video_path, video_id) + "*"):
            logging.info("Already Downloaded: " + url)
        else:
            # The ID, extracted from the embedding url, is put into the normal yt-url scheme.
            yt_url = "www.youtube.com/watch?v=%s" % video_id
            yt = YouTube(yt_url)
            if int(yt.length) <= length_cuttoff:
                stream = yt.streams \
                    .filter(progressive=True, file_extension='mp4') \
                    .order_by('resolution') \
                    .asc() \
                    .first()
                if stream.filesize <= size_cutoff:
                    stream.download(output_path=raw_video_path, filename=video_id)
                    logging.info("Success: " + url)
                else:
                    logging.info(("Too big (%s/%s): " % (stream.filesize, size_cutoff)) + url)
            else:
                logging.info(("Too long (%s/%s): " % (yt.length, length_cuttoff)) + url)
    except Exception as e:
        logging.error("Exception: %s %s" % (e, url))


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
