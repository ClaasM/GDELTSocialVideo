# crawl any websites that dont contain </html>

import psycopg2

from src.visualization.console import CrawlingProgress



def run():
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")

    c = conn.cursor()
    c.execute("SELECT DISTINCT video_id from article_videos WHERE platform='facebook'")
    videos = c.fetchall()

    for video_id, in videos:
        split = video_id.split("/")
        new_video_id = split[1] + "/" + split[0]
        c.execute("SELECT count(*) FROM videos WHERE id=%s AND platform='facebook'", [new_video_id])
        count, = c.fetchone()
        if count == 1:
            # This is one of the video_ids that are flipped
            c.execute("UPDATE article_videos SET video_id=%s WHERE video_id=%s AND platform='facebook'", [new_video_id, video_id])
            conn.commit()
    # Video_id for facebook videos in article_videos are flipped for some reason.


if __name__ == "__main__":
    run()