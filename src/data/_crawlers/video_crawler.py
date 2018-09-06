import os
from collections import Counter
from multiprocessing import Pool

from pytube import YouTube
from src.data.videos import video

from src.data.postgres.postgres_helper import PostgresHelper

raw_video_path = os.environ["DATA_PATH"] + "/raw/GDELT/videos/"
raw_article_path = os.environ["DATA_PATH"] + "/raw/GDELT/articles/"
GDELT_path = os.environ["DATA_PATH"] + "/external/GDELT/"


def download_yt_video(row):
    website_url, video_url = row
    video_id = video.get_id_from_yt_url(video_url)
    if not os.path.exists(os.path.join(raw_video_path, video_id)):
        try:
            YouTube(video_url) \
                .streams \
                .filter(progressive=True, file_extension='mp4') \
                .order_by('resolution') \
                .asc() \
                .first() \
                .download(output_path=raw_video_path, filename=video_id)
            return "Success"
        except Exception as e:
            print(str(e))
            return str(e)
    else:
        print("Already downloaded %s" % video_url)
        return "Already downloaded %s" % video_url


pool = Pool(8)
results = list()
usable_videos = list(PostgresHelper().usable_videos_iterator())
for result in pool.imap(download_yt_video, usable_videos):
    results.append(result)
    if len(results) % 10 == 0:
        print(len(results))
pool.close()
pool.join()

print(Counter(results))
