"""
TODO DRY
TODO refs and everything
TODO documentation
"""
import glob
import os
import tempfile
from multiprocessing.pool import Pool

import psycopg2
import zipfile, csv, io

import shutil

import src  # Needed s.t. DATA_PATH is set

conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
c = conn.cursor()

# Import every export CSV file
export_path = os.environ["DATA_PATH"] + "/external/export/"
unzipped_path = os.environ["DATA_PATH"] + "/interim/unzipped/"
files = glob.glob(export_path + "[0-9]*.export.csv.zip")
for file_path in files:
    archive = zipfile.ZipFile(file_path)
    # Unzip the file to a temporary csv
    # The temp file needs to be kept after closing because the COPY operation only works on closed files.
    with tempfile.NamedTemporaryFile(delete=False) as tmp, archive.open(archive.namelist()[0]) as file:
        shutil.copyfileobj(file, tmp)
        # write the unzipped csv to the database
        tmp_file = tmp.name
    # Put the csv into the database
    query = "COPY all_export FROM '%s' DELIMITER E'\t' CSV HEADER" % tmp_file
    print(query)
    c.execute(query)
    conn.commit()
    # Delete the temporary file
    os.remove(tmp_file)