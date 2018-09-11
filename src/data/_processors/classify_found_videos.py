"""
Takes all found videos and filters for those that pass the classifier as "relevant"
TODO and some more other filtering
TODO write documentation
"""
import os
from urllib.parse import urlparse

import psycopg2
from src import util


if __name__ == "__main__":
    video_dir = os.environ["DATA_DIR"] + "/external/video"
    tables = ["articles", "found_videos"]
    conn = psycopg2.connect(database="thesis", user="postgres")
    c = conn.cursor()
    for table in tables:
        # Create the new column
        c.execute('ALTER TABLE %s ADD COLUMN IF NOT EXISTS hostname TEXT' % table)
        conn.commit()

        # We're only interested in hosts that had any video etc. in them
        c.execute('SELECT website_url, hostname FROM %s' % table)
        for (website_url, hostname) in c.fetchall():
            # Website url may not be unique depending on the table, but it doesn't matter in this case
            if not hostname:
                new_hostname = urlparse(website_url).hostname
                c.execute('UPDATE %s SET hostname=\'%s\' WHERE website_url=\'%s\'' % (table, new_hostname, website_url))
                conn.commit()