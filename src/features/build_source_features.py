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


"""
  source_name                 TEXT NOT NULL,
  article_count               INT DEFAULT 0,
  -- Features are computed later
  twitter_video_std_dev       FLOAT,
  twitter_video_sum           INT,
  twitter_video_count         INT,
  twitter_video_sum_distinct  INT,
  youtube_video_std_dev       FLOAT,
  youtube_video_sum           INT,
  youtube_video_count         INT,
  youtube_video_sum_distinct  INT,
  facebook_video_std_dev      FLOAT,
  facebook_video_sum          INT,
  facebook_video_count        INT,
  facebook_video_sum_distinct INT,
  -- Relevancy is determined by the classifier
  twitter_relevant            BOOL,
  youtube_relevant            BOOL,
  facebook_relevant           BOOL,
"""

def run():
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    c.execute("SELECT * FROM sources LIMIT 1")
    if len(c.fetchall()) != 0:
        print("Sources table not empty, assuming it has already been populated...SKIPPED")
    else:
        # We're only interested in hosts that had any video etc. in them
        c.execute('SELECT DISTINCT hostname FROM found_videos')
        hosts = c.fetchall()
        for hostname in hosts:
            # print(hostname)
            hostname = hostname[0]
            features = dict()
            # article_count is already computed in when the db is populated

            # Get all videos from that hostname:
            c.execute('SELECT * FROM found_videos WHERE hostname=%s', [hostname])
            videos = c.fetchall()

            for platform in ["twitter", "youtube", "facebook"]:
                platform_videos = [video for video in videos if video[1] == platform]
                platform_videos_by_article = groupby(platform_videos, lambda video: video[0])

                video_counts = list(map(lambda videos: len(videos), platform_videos_by_article))
                video_counts += (features["article_count"] - len(video_counts)) * [0]

                features[platform + "_video_std_dev"] = np.std(video_counts) if len(video_counts) > 0 else -1
                # Number of articles that have 1+ videos
                c.execute("SELECT Count(DISTINCT (website_url)) FROM found_videos WHERE hostname=%s AND platform=%s",
                          [hostname, platform])
                features[platform + "_video_count"] = c.fetchone()[0]
                # Sum of videos in all articles
                features[platform + "_video_sum"] = len(platform_videos)
                features[platform + "_video_sum_distinct"] = len(set([video[2] for video in platform_videos]))

            c.execute(postgres_helper.dict_insert_string("hosts", features))
            conn.commit()

if __name__ == "__main__":
    run()
