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
c.execute('DROP TABLE IF EXISTS all_export')
c.execute('''CREATE TABLE all_export (
    -- Event ID and date attributes
    global_event_id BIGINT NOT NULL,
    sql_date INT NOT NULL,
    month_year INT NOT NULL,
    year INT NOT NULL,
    fraction_date FLOAT NOT NULL,
    -- Actor attributes
    actor1_code TEXT,
    actor1_name TEXT,
    actor1_country_code TEXT,
    actor1_known_group_code TEXT,
    actor1_ethnic_code TEXT,
    actor1_religion1_code TEXT,
    actor1_religion2_code TEXT,
    actor1_type1_code TEXT,
    actor1_type2_code TEXT,
    actor1_type3_code TEXT,
    actor2_code TEXT,
    actor2_name TEXT,
    actor2_country_code TEXT,
    actor2_known_group_code TEXT,
    actor2_ethnic_code TEXT,
    actor2_religion1_code TEXT,
    actor2_religion2_code TEXT,
    actor2_type1_code TEXT,
    actor2_type2_code TEXT,
    actor2_type3_code TEXT,
    -- Event action attributes
    is_root_event BOOL NOT NULL,
    event_code TEXT NOT NULL, -- These are "---" in very rare cases
    event_base_code TEXT NOT NULL,
    event_root_code TEXT NOT NULL,
    quad_class INT NOT NULL,
    goldstein_scale FLOAT, -- This is null in very rare cases (TODO statistic)
    num_mentions INT NOT NULL,
    num_sources INT NOT NULL,
    num_articles INT NOT NULL,
    avg_tone FLOAT NOT NULL,
    -- Event geography (actor 1)
    actor1_geo_type INT NOT NULL,
    actor1_geo_full_name TEXT,
    actor1_geo_country_code  TEXT,
    actor1_geo_ADM1_code TEXT,
    actor1_geo_ADM2_code TEXT,
    actor1_geo_lat FLOAT,
    actor1_geo_long FLOAT,
    actor1_geo_feature_id TEXT,
    -- Event geography (actor 2)
    actor2_geo_type INT NOT NULL,
    actor2_geo_fullName TEXT,
    actor2_geo__country_code TEXT,
    actor2_geo_ADM1_code TEXT,
    actor2_geo_ADM2_code TEXT,
    actor2_geo_lat TEXT,
    actor2_geo_long TEXT,
    actor2_geo_feature_id TEXT,
    -- Event geography (action)
    action_geo_type INT NOT NULL,
    action_geo_full_name TEXT,
    action_geo_country_code TEXT,
    action_geo_ADM1_code TEXT,
    action_geo_ADM2_code TEXT,
    action_geo_lat TEXT,
    action_geo_long TEXT,
    action_geo_feature_id TEXT,
    -- Data management
    date_added TEXT NOT NULL,
    source_url TEXT NOT NULL
);''')

# We need some indices to speed things up
c.execute('''CREATE INDEX IF NOT EXISTS all_export_global_event_id_index ON public.all_mentions (global_event_id);''')

conn.commit()

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

conn.commit()
