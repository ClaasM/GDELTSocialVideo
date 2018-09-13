import glob
import os
import tempfile
from multiprocessing.pool import Pool

import psycopg2
import zipfile, csv, io

import shutil

import src  # Needed s.t. DATA_PATH is set

conn = psycopg2.connect(database="thesis", user="postgres")
c = conn.cursor()

# Recreate the table
c.execute('DROP TABLE IF EXISTS all_mentions')
c.execute('''CREATE TABLE all_mentions (
  global_event_id     BIGINT NOT NULL,
  event_time_date     BIGINT NOT NULL,
  mention_time_date   BIGINT NOT NULL,
  mention_type        INT NOT NULL,
  mention_source_name TEXT,
  mention_identifier  TEXT,
  sentence_id         INT NOT NULL,
  actor1_char_offset  INT NOT NULL,
  actor2_char_offset  INT NOT NULL,
  action_char_offset  INT NOT NULL,
  in_raw_text         BOOL NOT NULL,
  confidence          FLOAT NOT NULL ,
  mention_doc_len     INT NOT NULL,
  mention_doc_tone    FLOAT NOT NULL,
  null_1 TEXT, --The CSV files have two empty tabs at the end of each line. These are dropped later.
  null_2 TEXT  --Postgres COPY cannot ignore columns in CSVs.
);''')
# We need some indices to speed things up
c.execute('''CREATE INDEX IF NOT EXISTS all_mentions_global_event_id_index ON public.all_mentions (global_event_id);''')

conn.commit()

# Import every mentions CSV file
mentions_path = os.environ["DATA_PATH"] + "/external/mentions/"
files = glob.glob(mentions_path + "[0-9]*.mentions.csv.zip")
for file_path in files:
    archive = zipfile.ZipFile(file_path)
    # Unzip the file to a temporary csv
    # The temp file needs to be kept after closing because the COPY operation only works on closed files.
    with tempfile.NamedTemporaryFile(delete=False) as tmp, archive.open(archive.namelist()[0]) as file:
        shutil.copyfileobj(file, tmp)
        # write the unzipped csv to the database
        tmp_file = tmp.name
    # Put the csv into the database
    query = "COPY all_mentions FROM '%s' DELIMITER E'\t' CSV HEADER" % tmp_file
    c.execute(query)
    conn.commit()
    # Delete the temporary file
    os.remove(tmp_file)


c.execute('ALTER TABLE all_mentions DROP COLUMN null_1')
c.execute('ALTER TABLE all_mentions DROP COLUMN null_2')
conn.commit()
