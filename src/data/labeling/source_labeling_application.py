"""
A small command line tool to make the labeling of relevancy of a a video for a certain topic easier.
"""

import psycopg2
from random import shuffle

from src.visualization import console

if __name__ == "__main__":
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()

    # Create a cursor for every source that hasn't been labeled yet.
    c.execute('''SELECT sources.source_name FROM sources 
        LEFT JOIN labeled_sources  ON labeled_sources.source_name = sources.source_name 
        WHERE labeled_sources.source_name IS NULL''')
    sourcenames = c.fetchall()
    shuffle(sourcenames)

    print(" Welcome to the source labeling application! ".upper().center(70, "*"))
    print()
    print("Please check the articles to determine,\n"
          "whether the videos embedded in the articles\n"
          "of that source are relevant to its content.")
    print()

    for source_name, in sourcenames:
        c.execute(
            '''SELECT article_videos.source_url, article_videos.platform FROM article_videos 
            WHERE source_name=%s''', [source_name])
        found_videos = c.fetchall()
        # We only need to label sources that actually have videos in them
        if len(found_videos) > 3:
            c.execute('''SELECT Count(1) FROM articles WHERE source_name=%s''',
                      [source_name])
            article_count, = c.fetchone()
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

            print("Total articles: %d, with embedding(s): %d" % (article_count, len(articles)))
            twitter_relevance = input(
                "Are the source's TWITTER tweets relevant? (1: Yes, 2: No (e.g. in sidebar), 3: No (user-created)), 4: No (other/not present) ") if "twitter" in found_platforms else -1
            facebook_relevance = input(
                "Are the source's FACEBOOK videos relevant? (1: Yes, 2: No (e.g. in sidebar), 3: No (user-created)), 4: No (other/not present) ") if "facebook" in found_platforms else -1
            youtube_relevance = input(
                "Are the source's YOUTUBE videos relevant? (1: Yes, 2: No (e.g. in sidebar), 3: No (user-created)), 4: No (other/not present) ") if "youtube" in found_platforms else -1

            c.execute(
                '''INSERT INTO labeled_sources (source_name, youtube_relevant, twitter_relevant, facebook_relevant) VALUES (%s, %s, %s, %s)''',
                [source_name, youtube_relevance, twitter_relevance, facebook_relevance])
            conn.commit()
            print()
