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
    c.execute('ALTER TABLE articles ADD COLUMN IF NOT EXISTS hostname TEXT')
    conn.commit()
    # We're only interested in hosts that had any video etc. in them
    c.execute('SELECT * FROM articles')
    for website_url, status, hostname in c.fetchall():
        # Website url is not unique, but it doesn't matter in this case
        new_hostname = urlparse(website_url).hostname
        c.execute('UPDATE articles SET hostname=%s WHERE website_url=%s', [new_hostname, website_url])
    conn.commit()

