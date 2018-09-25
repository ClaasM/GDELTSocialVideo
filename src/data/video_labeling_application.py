"""
A small command line tool to make the labeling videos easier.
Possible labels are: amateur (0), edited (1), professional (2)
Whereas edit videos might include snippets of amateur footage with voice overlay, e.g. news reports,
and professional does not include any amateur footage (e.g. music videos, movie trailers)

TODO What percentage is already covered by amateur, news, trailer, music,


TODO print introduction or something
TODO also print total number of videos already labeled
"""

import psycopg2
from random import shuffle

from src.visualization import console

if __name__ == "__main__":
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS labeled_videos (
                  id TEXT PRIMARY KEY,
                  type INTEGER)''')
    conn.commit()

    # Create a cursor for every video that hasn't been labeled yet.
    # TODO continue here
    c.execute(
        '''SELECT id FROM hosts LEFT JOIN labeled_hosts  ON labeled_hosts.hostname = hosts.hostname WHERE labeled_hosts.hostname IS NULL''')
    hostnames = c.fetchall()
    shuffle(hostnames)

    for hostname in hostnames:
        hostname = hostname[0]
        c.execute('''SELECT found_videos.website_url, found_videos.platform FROM found_videos WHERE hostname=%s''',
                  [hostname])
        found_videos = c.fetchall()
        c.execute('''SELECT Count(1) FROM articles WHERE hostname=%s''',
                  [hostname])
        article_count = c.fetchone()[0]
        articles = dict()
        found_platforms = set()
        for url, platform in found_videos:
            if url not in articles:
                articles[url] = {"twitter": 0, "facebook": 0, "youtube": 0}
            articles[url][platform] += 1
            found_platforms.add(platform)

        table_printer = console.TablePrinter(["twitter", "facebook", "youtube", "URL"])
        for url in articles.keys():
            counts = articles[url]
            table_printer.print_row([counts["twitter"], counts["facebook"], counts["youtube"], url])

        # TODO interate over platforms here
        print("Total articles: %d, with embedding(s): %d" % (article_count, len(articles)))
        twitter_relevance = input(
            "Are the host's TWITTER tweets relevant? (1: Yes, 2: No (e.g. in sidebar), 3: No (user-created)), 4: No (not present) ") if "twitter" in found_platforms else -1
        facebook_relevance = input(
            "Are the host's FACEBOOK videos relevant? (1: Yes, 2: No (e.g. in sidebar), 3: No (user-created)), 4: No (not present) ") if "facebook" in found_platforms else -1
        youtube_relevance = input(
            "Are the host's YOUTUBE videos relevant? (1: Yes, 2: No (e.g. in sidebar), 3: No (user-created)), 4: No (not present) ") if "youtube" in found_platforms else -1

        c.execute(
            '''INSERT INTO labeled_hosts (hostname, youtube_relevant, twitter_relevant, facebook_relevant) VALUES (%s, %s, %s, %s)''',
            [hostname, youtube_relevance, twitter_relevance, facebook_relevance])
        conn.commit()
        print()
