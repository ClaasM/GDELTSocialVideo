from urllib.parse import urlparse

import psycopg2
from src import util

"""
TODO write documentation
"""

if __name__ == "__main__":
    conn = psycopg2.connect(database="thesis", user="postgres")
    c = conn.cursor()
    # Create the new column
    c.execute('ALTER TABLE found_videos ADD COLUMN IF NOT EXISTS hostname TEXT')
    conn.commit()
    # We're only interested in hosts that had any video etc. in them
    c.execute('SELECT * FROM found_videos')
    #return len(self.c.fetchall()) > 0
    for website_url, platform, video_url, hostname in c.fetchall():
        # Website url is not unique, but it doesn't matter in this case
        new_hostname = urlparse(website_url).hostname
        c.execute('UPDATE found_videos SET hostname=%s WHERE website_url=%s', [new_hostname, website_url])
    conn.commit()

