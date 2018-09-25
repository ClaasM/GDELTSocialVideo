# TODO move all article files
# AND set every file that has success but doesnt exists/isn't HTML to "Not crawled"
# AND recrawl
# AND implement this in the article crawler

import glob
import os
import tarfile
import psycopg2
from src.data.videos import video as video_helper
from src.data.websites import website as website_helper


conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
c = conn.cursor()
c.execute("SELECT DISTINCT source_url from article_videos")

videos = c.fetchall()

print(len(videos))

counter = {False:0,True:0}

for index, video in enumerate(videos):
    if index % 10000 == 0:
        print(index)
        print(counter)
    path, name = website_helper.get_article_filepath(video[0])
    exists = os.path.exists(path + "/" + name)
    if not exists:
        print(video[0])
        print(path)
    counter[exists] += 1

print(counter)

# videos = glob.glob(videos_path + "/*.mp4")
# print(len(videos))

# for video_path in videos:
#    video_id = video_path.split("/")[-1].split(".")[0]
#    c.execute("UPDATE videos SET crawling_status='Success' WHERE id=%s", [video_id])
#    conn.commit()
