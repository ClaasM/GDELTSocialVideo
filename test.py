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


with tarfile.open(os.environ["DATA_PATH"] + "/raw/articles.tar") as tf:
    for index, file in enumerate(tf):
        if index % 10000 == 0:
            print(index)
        if file.isfile():
            old_file_name = file.name[9:] # remove the "articles/"
            url = website_helper.url_decode(old_file_name)
            new_file_path, new_file_name = website_helper.get_article_filepath(url)
            if not os.path.exists(new_file_path):
                os.makedirs(new_file_path)
            tf.extract(file)
            os.rename(file.name, new_file_path + "/" +  new_file_name)

#conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
#c = conn.cursor()

#videos_path = video_helper.get_path("youtube")
#videos = glob.glob(videos_path + "/*.mp4")
#print(len(videos))

#for video_path in videos:
#    video_id = video_path.split("/")[-1].split(".")[0]
#    c.execute("UPDATE videos SET crawling_status='Success' WHERE id=%s", [video_id])
#    conn.commit()