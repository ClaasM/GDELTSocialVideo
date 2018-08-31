import sqlite3
import os

"""
TODO stuff like required columns, indexing, etc.
"""


class SQLiteHelper:
    def __init__(self, ):
        self.conn = sqlite3.connect(os.environ["DATA_PATH"] + '/interim/GDELT.db')
        self.c = self.conn.cursor()

    def is_crawled(self, website_url):
        """Checks if a website_url has already been successfully crawled."""
        return self.c.execute('''SELECT 1 FROM crawled_websites WHERE website_url=\'%s\'''' % website_url) \
                   .fetchone() is not None

    def has_videos(self, website_url):
        return self.c.execute('''SELECT 1 FROM found_videos WHERE website_url=\'%s\'''' % website_url) \
                   .fetchone() is not None

    def save_crawled(self, website_url):
        self.c.execute('''INSERT INTO crawled_websites VALUES (\'%s\')''' % website_url)
        self.conn.commit()

    def save_mention(self, event_id, website_url):
        self.c.execute('''INSERT INTO mention VALUES (%d, \'%s\')''' % (event_id, website_url))
        self.conn.commit()

    def save_found_video(self, website_url, video_id):
        self.c.execute('''INSERT INTO found_videos VALUES (\'%s\',\'%s\')''' % (website_url, video_id))
        self.conn.commit()
