# TODO move all article files
# AND set every file that has success but doesnt exists to "Not crawled"
# AND recrawl

import glob

import psycopg2
from src.data.videos import video as video_helper
from src.data.websites import website as website_helper


conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
c = conn.cursor()

videos_path = video_helper.get_path("youtube")
videos = glob.glob(videos_path + "/*.mp4")
print(len(videos))

for video_path in videos:
    video_id = video_path.split("/")[-1].split(".")[0]
    c.execute("UPDATE videos SET crawling_status='Success' WHERE id=%s", [video_id])
    conn.commit()