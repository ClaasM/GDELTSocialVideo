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

path = os.environ["DATA_PATH"] + "/raw/articles/"
files = os.listdir(path)

for index, file in enumerate(files):
    if index % 10000 == 0:
        print(index)
    url = website_helper.url_decode(file)
    new_file_path, new_file_name = website_helper.get_article_filepath(url)
    if not os.path.exists(new_file_path):
        os.makedirs(new_file_path)
    os.rename(path + file, new_file_path + "/" + new_file_name)


# conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
# c = conn.cursor()

# videos_path = video_helper.get_path("youtube")
# videos = glob.glob(videos_path + "/*.mp4")
# print(len(videos))

# for video_path in videos:
#    video_id = video_path.split("/")[-1].split(".")[0]
#    c.execute("UPDATE videos SET crawling_status='Success' WHERE id=%s", [video_id])
#    conn.commit()
