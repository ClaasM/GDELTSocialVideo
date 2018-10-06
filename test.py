# crawl any websites that dont contain </html>
import re

import psycopg2
import sys

from src.data.videos import video as video_helper
from src.data.websites import website as website_helper

conn = psycopg2.connect(database="gdelt_social_video", user="postgres")

c = conn.cursor()
c.execute("SELECT DISTINCT source_url from article_videos")
articles = c.fetchall()

print(len(articles))
counter = {True: 0, False: 0}

for index, (source_url,) in enumerate(articles):
    if index % 10000 == 0:
        print(index)
        print(counter)
    path = website_helper.get_article_filepath(source_url)
    article = website_helper.load(source_url)
    # Assuming that if it contains a closing tag, it is HTML
    counter[bool(re.search(r'</[a-zA-Z]+>', article))] +=1

print(counter)

