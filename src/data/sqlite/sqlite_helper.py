import sqlite3
import os

"""
TODO stuff like required columns, indexing, etc.
"""

SUCCESS = "Success"


class SQLiteHelper:
    def __init__(self, ):
        self.conn = sqlite3.connect(os.environ["DATA_PATH"] + '/interim/GDELT.db')
        self.c = self.conn.cursor()

    def is_crawled(self, website_url):
        """Checks if a website_url has already been successfully crawled."""
        # TODO AND status=\'Success\' omitted for now. We don't try again yet.
        return self.c.execute('''SELECT 1 FROM crawled_websites WHERE website_url=?''', [website_url]) \
                   .fetchone() is not None

    def has_videos(self, website_url):
        return self.c.execute('''SELECT 1 FROM found_videos WHERE website_url=?''', [website_url]) \
                   .fetchone() is not None

    def save_crawled(self, website_url, status=SUCCESS):
        self.c.execute('''INSERT INTO crawled_websites VALUES (?, ?)''', (website_url, status))
        self.conn.commit()

    def save_mention_with_video(self, event_id, website_url):
        self.c.execute('''INSERT INTO mentions VALUES (?, ?)''', (event_id, website_url))
        self.conn.commit()

    def save_found_video_url(self, website_url, platform, video_url):
        self.c.execute('''INSERT INTO found_videos VALUES (?,?,?)''', (website_url, platform, video_url))
        self.conn.commit()

    def save_usable_video_url(self, website_url, video_url):
        self.c.execute('''INSERT INTO usable_videos VALUES (?,?)''', (website_url, video_url))
        self.conn.commit()

    def usable_videos_iterator(self):
        return self.c.execute('SELECT * FROM usable_videos')
