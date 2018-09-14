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

# Add the columns to "catch" the null values at the end of each line in the CSVs
# Postgres COPY cannot specify which columns to import, its all or nothing. These are dropped at the end of the script.
c.execute('''ALTER TABLE all_mentions ADD COLUMN null_1 TEXT, ADD COLUMN null_2 TEXT''')
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
    print(query)
    c.execute(query)
    conn.commit()
    # Delete the temporary file
    os.remove(tmp_file)

# Drop the empty columns again
c.execute('ALTER TABLE all_mentions DROP COLUMN null_1, DROP COLUMN null_2')
conn.commit()
