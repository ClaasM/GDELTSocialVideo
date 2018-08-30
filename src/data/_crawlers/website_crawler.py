"""
Crawls all websites and saves which websites were successfully crawled.
Saved each found embedded youtube video id to the database
"""

from gzip import GzipFile
import pandas as pd
from src.data import webpage

data_dir = "../../data/"

# Global configuration variables
data_count = 10000 # The number of rows (=articles) to read

# Read the first (of 7) parts of the dataset.
with GzipFile(data_dir + '/external/vgkg-20160427-part1.csv.gz') as gzipfile:
    df = pd.read_csv(gzipfile, nrows=data_count)

    def task(row):
        index, (date, document_identifier, image_URL, raw_JSON) = row
        doc = webpage.download_rendered(document_identifier)
        print(doc.keys())

