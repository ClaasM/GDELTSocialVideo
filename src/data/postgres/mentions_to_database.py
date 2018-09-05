import glob
import os
from multiprocessing.pool import Pool

import psycopg2
import zipfile, csv, io
import src # Needed s.t. DATA_PATH is set

conn = psycopg2.connect(database="thesis", user="postgres")
c = conn.cursor()
c.execute('DELETE FROM all_mentions')
conn.commit()
mentions_path = os.environ["DATA_PATH"] + "/external/GDELT/mentions/"
files = glob.glob(mentions_path + "[0-9]*.mentions.csv.zip")


def write_to_db(filepath):
    archive = zipfile.ZipFile(filepath)
    file = archive.open(archive.namelist()[0])
    reader = csv.reader(io.TextIOWrapper(file), delimiter='\t')
    for row in reader:
        global_event_id, mention_identifier, confidence = row[0], row[5], row[11]
        c.execute('INSERT INTO all_mentions VALUES (%s)', [mention_identifier])
        conn.commit()
    file.close()
    archive.close()


pool = Pool(8)  # 16 seems to be around optimum
count = 0
for _ in pool.imap_unordered(write_to_db, files):
    count += 1
pool.close()
pool.join()
