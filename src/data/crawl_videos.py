from multiprocessing import Pool
from random import shuffle

import sys
import psycopg2

from src.data.postgres import postgres_helper
from src.data.videos import youtube, twitter, facebook
from src.visualization.console import CrawlingProgress


def download_video(args):
    video_id, platform = args

    try:
        # TODO use subscripts here
        if platform == "youtube":
            video = youtube.download(video_id)
        elif platform == "twitter":
            video = twitter.download(video_id)
        else:  # if platform == "facebook":
            video = facebook.download(video_id)
        video["id"] = video_id
    except Exception as e:
        print(e)
        video = {"crawling_status": str(e)} # Can't extract id from video
    return video


def run():
    # We create a Pool (of Threads, not processes, since, again, this task is I/O-bound anyways)
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    # TODO or Player Config: 429, or Player Config: 403 when doing this for twitter
    c.execute("""SELECT id, platform FROM videos WHERE crawling_status='Not Crawled' AND platform = 'facebook'""") # AND platform='twitter'
    videos = c.fetchall()#[:10000]
    shuffle(videos)

    print(len(videos))

    pool = Pool(16)
    crawling_progress = CrawlingProgress(len(videos), update_every=100)
    for video in pool.imap_unordered(download_video, videos):
        if video["crawling_status"] == "Player Config: 429":
            print("Twitter rate limit hit. Try again in 15 minutes")
            sys.exit(1)
        query = ("UPDATE videos SET %s" % postgres_helper.dict_mogrifying_string(video)) + " WHERE id=%(id)s"
        c.execute(query, video)
        conn.commit()
        crawling_progress.inc(by=1)
    pool.close()
    pool.join()


if __name__ == "__main__":
    run()
