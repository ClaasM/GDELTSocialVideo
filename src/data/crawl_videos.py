from multiprocessing import Pool
from random import shuffle

import psycopg2

from src.data.postgres import postgres_helper
from src.data.videos import youtube, twitter, facebook
from src.visualization.console import CrawlingProgress


def download_video(args):
    url, platform = args
    if platform == "youtube":
        video_id = youtube.get_id_from_url(url)
        video = youtube.download(video_id)
    elif platform == "twitter":
        video_id = twitter.get_id_from_url(url)
        video = twitter.download(video_id)
    else:  # if platform == "facebook":
        video_id, user_name = facebook.get_id_from_url(url)
        video = facebook.download(video_id, user_name)
    video["id"] = video_id
    video["url"] = url
    return video


def run():
    # We create a Pool (of Threads, not processes, since, again, this task is I/O-bound anyways)
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    c.execute("SELECT url, platform FROM videos WHERE crawling_status = 'Not Crawled' AND platform='facebook'")
    videos = c.fetchall()
    shuffle(videos)
    videos = videos[:1000]

    pool = Pool(4)
    crawling_progress = CrawlingProgress(len(videos), update_every=10)
    for video in pool.imap_unordered(download_video, videos):
        print(video)
        query = ("UPDATE videos SET %s" % postgres_helper.dict_mogrifying_string(video)) + " WHERE url=%(url)s"
        c.execute(query, video)
        conn.commit()
        crawling_progress.inc(by=1)
    pool.close()
    pool.join()


if __name__ == "__main__":
    run()
