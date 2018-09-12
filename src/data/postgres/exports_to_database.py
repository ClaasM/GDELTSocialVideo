import glob
import os
import tempfile
from multiprocessing.pool import Pool

import psycopg2
import zipfile, csv, io

import shutil

import src  # Needed s.t. DATA_PATH is set

"""
TODO DRY
TODO refs and everything
"""
conn = psycopg2.connect(database="thesis", user="postgres")
c = conn.cursor()

# Recreate the table
c.execute('DROP TABLE IF EXISTS all_exports')
c.execute('''CREATE TABLE all_exports (
  ["GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate", "Actor1Code", "Actor1Name",
          "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode", "Actor1Religion1Code",
          "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code", "Actor2Code",
          "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode", "Actor2EthnicCode", "Actor2Religion1Code",
          "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code", "IsRootEvent",
          "EventCode", "EventBaseCode", "EventRootCode", "QuadClass", "GoldsteinScale", "NumMentions",
          "NumSources", "NumArticles", "AvgTone", "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
          "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
          "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code",
          "Actor2Geo_ADM2Code", "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID", "ActionGeo_Type",
          "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code", "ActionGeo_ADM2Code",
          "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID", "DATEADDED", "SOURCEURL"]


  null_1 TEXT, --The CSV files have two empty tabs at the end of each line. These are dropped later.
  null_2 TEXT  --Postgres COPY cannot ignore columns in CSVs. TODO might not need this here
);''')
# We need some indices to speed things up
c.execute('''CREATE INDEX IF NOT EXISTS all_mentions_global_event_id_index ON public.all_mentions (global_event_id);''')

conn.commit()

# Import every mentions CSV file
mentions_path = os.environ["DATA_PATH"] + "/external/mentions/"
unzipped_path = os.environ["DATA_PATH"] + "/interim/unzipped/"
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
