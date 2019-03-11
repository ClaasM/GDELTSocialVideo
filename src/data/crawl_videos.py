"""
Crawls all not-yet crawled videos
"""
from multiprocessing import Pool
from random import shuffle

import sys
import psycopg2

from src.data.postgres import postgres_helper
from src.data.videos import youtube, twitter, facebook
from src.visualization.console import StatusVisualization


def download_video(args):
    video_id, platform = args

    try:
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


def run(db, user):
    # We create a Pool (of Threads, not processes, since, again, this task is I/O-bound anyways)
    conn = psycopg2.connect(database=db, user=user)
    c = conn.cursor()
    c.execute("""SELECT id, platform FROM videos WHERE crawling_status='Not Crawled'""")
    videos = c.fetchall()#[:10000]
    shuffle(videos)

    print(len(videos))

    pool = Pool(16)
    crawling_progress = StatusVisualization(len(videos), update_every=100)
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


import argparse

parser = argparse.ArgumentParser(description='Crawls articles in the articles table of a specified database.')

parser.add_argument('--db', help='Database containing the videos. Default: "gdelt_social_video"', type=str,
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

