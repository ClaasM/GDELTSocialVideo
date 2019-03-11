from urllib.parse import urlparse

import psycopg2
from src import util

"""
THIS IS OBSOLETE.
It was used to extract source names for the articles and the videos found in them 
when that wasn't yet done immediately during crawling.
"""

if __name__ == "__main__":
    tables = ["articles", "article_videos"]
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    for table in tables:
        # Create the new column
        c.execute('ALTER TABLE %s ADD COLUMN IF NOT EXISTS source_name TEXT' % table)
        conn.commit()

        # We're only interested in hosts that had any video etc. in them
        c.execute('SELECT source_url, source_name FROM %s' % table)
        for (source_url, source_name) in c.fetchall():
            # Website url may not be unique depending on the table, but it doesn't matter in this case
            if not source_name:
                new_hostname = urlparse(source_url).hostname
                c.execute('UPDATE %s SET source_name=\'%s\' WHERE source_url=\'%s\'' % (table, new_hostname, source_url))
                conn.commit()