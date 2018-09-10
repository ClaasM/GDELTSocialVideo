"""
Computes the features used to classify whether or not the videos on a hosts website are relevant.
The columns for whether the host's videos from a specific platform are deemed relevant are created but filled at a later point.

Features per host and per platform (facebook, twitter, youtube):
- video_count_std_dev: Deviation in the number of videos per article
- video_count_sum: Total number of videos across all articles
- video_count_sum_distinct: Total number of distinct videos across all articles

Features per host:
- article_count: The number of articles from that host, including those that don't contain videos

Features that can easily be computed from these features, thus are not calculated yet:
- Average: Average number of videos per article, including articles without videos
- Average distinct videos per article
- Distinct videos to total videos

Hypothesis:
- High average but low distinct count means
"""
import numpy as np
import psycopg2
from itertools import groupby
from src.data.postgres import postgres_helper

if __name__ == "__main__":
    conn = psycopg2.connect(database="thesis", user="postgres")
    c = conn.cursor()
    # Create the new table
    c.execute('DROP TABLE IF EXISTS hosts')
    c.execute('''CREATE TABLE hosts (
        hostname TEXT,
        article_count INT,
        
        twitter_video_count_std_dev FLOAT,
        twitter_video_count_sum INT,
        twitter_video_count_sum_distinct INT,
        
        youtube_video_count_std_dev FLOAT,
        youtube_video_count_sum INT,
        youtube_video_count_sum_distinct INT,
        
        facebook_video_count_std_dev FLOAT,
        facebook_video_count_sum INT,
        facebook_video_count_sum_distinct INT,

        twitter_relevant BOOL,
        youtube_relevant BOOL,
        facebook_relevant BOOL
    )''')
    # Create indices if they do not exist to speed things up a little
    c.execute('''CREATE INDEX IF NOT EXISTS articles_hostname_index ON public.articles (hostname);''')
    c.execute('''CREATE INDEX IF NOT EXISTS articles_found_videos_index ON public.found_videos (hostname);''')

    conn.commit()
    # We're only interested in hosts that had any video etc. in them
    c.execute('SELECT DISTINCT hostname FROM found_videos')
    hosts = c.fetchall()
    for hostname in hosts:
        #print(hostname)
        hostname = hostname[0]
        features = dict()
        features["hostname"] = hostname

        # Get article count from that hostname:
        c.execute('SELECT Count(*) FROM articles WHERE hostname=%s', [hostname])
        features["article_count"] = c.fetchone()[0]

        # Get all videos from that hostname:
        c.execute('SELECT * FROM found_videos WHERE hostname=%s', [hostname])
        videos = c.fetchall()

        for platform in ["twitter", "youtube", "facebook"]:
            platform_videos = [video for video in videos if video[1] == platform]
            platform_videos_by_article = groupby(platform_videos, lambda video: video[0])


            video_counts = list(map(lambda videos: len(videos), platform_videos_by_article))
            video_counts += (features["article_count"] - len(video_counts)) * [0]

            features[platform + "_video_count_std_dev"] = np.std(video_counts) if len(video_counts) > 0 else -1
            features[platform + "_video_count_sum"] = len(platform_videos)
            features[platform + "_video_count_sum_distinct"] = len(set([video[2] for video in platform_videos]))

        c.execute(postgres_helper.dict_insert_string("hosts",features))
        conn.commit()


    # First, lets get all articles from each

"""
TODO rename:
articles --> articles
merge mentions and all_mentions (maybe?)
"""
