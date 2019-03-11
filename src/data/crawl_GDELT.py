#! /Library/Frameworks/Python.framework/Versions/3.5/bin/python3

"""
Downloads all exports and mentions for a month.
Make sure a master file containing the requested dates is present.
The current master file can be downloaded from: http://data.gdeltproject.org/gdeltv2/masterfilelist.txt
See GDELT Docs for more info.
"""

import os
import urllib.request
from multiprocessing import Pool
from src.visualization.console import StatusVisualization

INTERESTING_COLLECTIONS = ["mentions", "export"]


def run(year, month):
    # Make sure the data directories for the interesting collections exist.
    for collection in INTERESTING_COLLECTIONS:
        path = "%s/external/%s/" % (os.environ["DATA_PATH"], collection)
        if not os.path.exists(path):
            os.makedirs(path)

    with open(os.environ["DATA_PATH"] + "/external/masterfilelist.txt") as master_file_list:

        urls = list()
        malformed_lines = 0
        relevant_lines = 0

        for line in master_file_list:
            # Example line: 134072 f1c7a45aa0292b0aee2bc5b674841096 http://data.gdeltproject.org/gdeltv2/20180731191500.export.CSV.zip
            # But some files are missing, then the master file just contains http://data.gdeltproject.org/gdeltv2/
            try:
                url = line.rstrip("\n").split(" ")[2]
                file_name = url.split("/")[-1].lower()  # Casing is inconsistent in the data source, we don't want that
                # Correct time?
                if file_name.startswith("%d%02d" % (year, month)):
                    relevant_lines += 1
                    # One of the collections we're interested in?
                    collection = file_name.split(".")[-3]
                    if collection in INTERESTING_COLLECTIONS:
                        file_path = "%s/external/%s/%s" % (os.environ["DATA_PATH"], collection, file_name)
                        # Not already downloaded?
                        # if not os.path.isfile(file_path):
                        urls.append((url, file_path))
                elif file_name.startswith("%d%02d" % (year, month + 1)):
                    # We're done. (the dates are in order in the master file)
                    break
            except Exception as e:
                malformed_lines += 1  # Some lines just contain http://data.gdeltproject.org/gdeltv2/

        print("\nDone reading the master file.\n")
        print("%d relevant files,\n %d malformed,\n %d already downloaded,\n %d now downloading...\n" \
              % (relevant_lines, malformed_lines, relevant_lines - len(urls), len(urls)))

        crawling_progress = StatusVisualization(len(urls), update_every=50)
        with Pool(16) as pool:
            for _ in pool.imap_unordered(retrieve_and_save, urls):
                crawling_progress.inc()


def retrieve_and_save(element):
    try:
        urllib.request.urlretrieve(element[0], element[1])
    except KeyboardInterrupt:
        pass
    return 1


import argparse

parser = argparse.ArgumentParser(description="Downloads the GDELT dataset for a given month.")

parser.add_argument('year', help='Which year of the dataset to download', type=int)
parser.add_argument('month', nargs='+', help='Which month(s) of the dataset to download', type=int)

parser.add_argument('--masterfile', help='Path to the Master file (default: masterfilelist.txt)',
                    default="masterfilelist.txt")
parser.add_argument('--out', help='Path to save the dataset to (default: ./data)', default="./data")

args = parser.parse_args()

if __name__ == "__main__":
    try:
        run(args.year, args.month[0])
    except KeyboardInterrupt:
        print("Interrupted by user. To resume, run again.")
        pass
