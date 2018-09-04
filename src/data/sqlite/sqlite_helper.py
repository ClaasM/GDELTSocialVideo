import mysql.connector
import os

"""
TODO stuff like required columns, indexing, etc.
"""

SUCCESS = "Success"


class SQLiteHelper:
    def __init__(self, ):
        :
        self.conn = mysql.connector.connect(
            host=os.environ["MYSQL_HOST"] if "MYSQL_HOST" in os.environ else "localhost",
            password=os.environ["MYSQL_PASSWORD"] if "MYSQL_PASSWORD" in os.environ else "",
            user=os.environ["MYSQL_USER"] if "MYSQL_USER" in os.environ else "root",
            database="thesis"
        )
        self.c = self.conn.cursor()

    def is_crawled(self, website_url):
        """Checks if a website_url has already been successfully crawled."""
        # TODO AND status=\'Success\' omitted for now. We don't try again yet.
        self.c.execute('SELECT 1 FROM crawled_websites WHERE website_url=%s LIMIT 1', [website_url])
        return len(self.c.fetchall()) > 0

    def has_videos(self, website_url):
        self.c.execute('SELECT 1 FROM found_videos WHERE website_url=%s LIMIT 1', [website_url])
        return len(self.c.fetchall()) > 0

    def save_crawled(self, website_url, status=SUCCESS):
        self.c.execute('INSERT INTO crawled_websites VALUES (%s, %s)', (website_url, status))
        self.conn.commit()

    def save_mention_with_video(self, event_id, website_url):
        self.c.execute('INSERT INTO mentions VALUES (%s, %s)', (event_id, website_url))
        self.conn.commit()

    def save_found_video_url(self, website_url, platform, video_url):
        self.c.execute('INSERT INTO found_videos VALUES (%s,%s,%s)', (website_url, platform, video_url))
        self.conn.commit()

    def save_usable_video_url(self, website_url, video_url):
        self.c.execute('INSERT INTO usable_videos VALUES (%s,%s)', (website_url, video_url))
        self.conn.commit()

    def usable_videos_iterator(self):
        self.c.execute('SELECT * FROM usable_videos')
        return self.c
