import glob
import os
import shutil
import tempfile
import zipfile

import psycopg2

from src.visualization.console import SyncedCrawlingProgress
from src import util


def zipped_csv_to_db(file_path, table, cursor):
    archive = zipfile.ZipFile(file_path)
    # Unzip the file to a temporary csv
    # The temp file needs to be kept after closing because the COPY operation only works on closed files.
    with tempfile.NamedTemporaryFile(delete=False) as tmp, archive.open(archive.namelist()[0]) as file:
        shutil.copyfileobj(file, tmp)
        # write the unzipped csv to the database
        tmp_file = tmp.name
    # Make sure the database has access to the file
    os.chmod(tmp_file, 0o777)
    # Put the csv into the database using postgres COPY
    query = "COPY %s FROM '%s' DELIMITER E'\t' CSV HEADER" % (table, tmp_file)
    cursor.execute(query)
    # Delete the temporary file
    os.remove(tmp_file)


def run():
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()

    """ IMPORT "EXPORT" DATASET (1/2) """

    c.execute("SELECT * FROM events LIMIT 1")
    if len(c.fetchall()) != 0:
        print("Event table not empty, assuming it has already been populated...SKIPPED")
    else:
        print(" IMPORTING 'EXPORT' DATA (1/2) ".center(77, "="))
        files = glob.glob(os.environ["DATA_PATH"] + "/external/export/[0-9]*.export.csv.zip")
        crawling_progress = SyncedCrawlingProgress(total_count=len(files), update_every=100)  # Keep track of progress
        for file_path in files:
            # put the csv into the database
            zipped_csv_to_db(file_path, "events", c)
            conn.commit()
            crawling_progress.inc()

    """ IMPORT "MENTIONS" DATASET """

    c.execute("SELECT * FROM mentions LIMIT 1")
    if len(c.fetchall()) != 0:
        print("Mentions table not empty, assuming it has already been populated...SKIPPED")
    else:
        # Add the columns to "catch" the null values at the end of each line in the CSVs
        # Postgres COPY cannot specify which columns to import, its all or nothing. These are dropped at the end of the script.
        c.execute('ALTER TABLE mentions ADD COLUMN null_1 TEXT, ADD COLUMN null_2 TEXT')
        conn.commit()

        print(" IMPORTING 'MENTIONS' DATA (2/2) ".center(77, "="))
        files = glob.glob(os.environ["DATA_PATH"] + "/external/mentions/[0-9]*.mentions.csv.zip")
        crawling_progress = SyncedCrawlingProgress(total_count=len(files), update_every=100)  # Keep track of progress
        for file_path in files:
            # put the csv into the database
            zipped_csv_to_db(file_path, "mentions", c)
            crawling_progress.inc()

        # Drop the empty columns again
        c.execute('ALTER TABLE mentions DROP COLUMN null_1, DROP COLUMN null_2')
        conn.commit()

    """ CREATE "ARTICLES" TABLE """

    c.execute("SELECT * FROM articles LIMIT 1")
    if len(c.fetchall()) != 0:
        print("Articles table not empty, assuming it has already been populated...SKIPPED")
    else:
        print(" CREATING 'ARTICLES' TABLE (3/3) ".center(77, "="))
        mentions_cursor = conn.cursor()
        mentions_cursor.execute("SELECT mention_identifier, mention_source_name  FROM mentions WHERE mention_source_name NOTNULL")
        c.execute("SELECT Count(1) FROM mentions")
        crawling_progress = SyncedCrawlingProgress(total_count=c.fetchone()[0], update_every=100000)  # Keep track of progress
        for article in mentions_cursor:
            crawling_progress.inc()
            mention_identifier, mention_source_name = article
            # Mentions are not always from a website, so MentionIdentifier is not always a URL. Those that aren't are skipped.
            if util.is_url(mention_identifier):
                c.execute("""INSERT INTO articles (source_url, source_name) VALUES (%s, %s)
                              ON CONFLICT (source_url) DO NOTHING""", [mention_identifier, mention_source_name])
                conn.commit()

    # The sources tables are populated during crawling (because we only keep those sources with videos)


if __name__ == "__main__":
    run()
