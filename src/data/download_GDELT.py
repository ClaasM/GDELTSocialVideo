"""
Downloads all exports and mentions for a month.
Make sure a master file containing the requested dates is present.
The current master file can be downloaded from: http://data.gdeltproject.org/gdeltv2/masterfilelist.txt
See GDELT Docs for more info.

TODO use crawling progress

"""

import os
import urllib.request
from multiprocessing import Pool
import src

YEAR = 2018
MONTH = 7
INTERESTING_COLLECTIONS = ["mentions", "export"]


def run():
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
                if file_name.startswith("%d%02d" % (YEAR, MONTH)):
                    relevant_lines += 1
                    # One of the collections we're interested in?
                    collection = file_name.split(".")[-3]
                    if collection in INTERESTING_COLLECTIONS:
                        file_path = "%s/external/%s/%s" % (os.environ["DATA_PATH"], collection, file_name)
                        # Not already downloaded?
                        if not os.path.isfile(file_path):
                            urls.append((url, file_path))
                elif file_name.startswith("%d%02d" % (YEAR, MONTH + 1)):
                    # We're done. (the dates are in order in the master file)
                    break
            except Exception as e:
                malformed_lines += 1  # Some lines just contain http://data.gdeltproject.org/gdeltv2/

        print("%d relevant lines, %d malformed, %d already downloaded, %d now downloading..." \
              % (relevant_lines, malformed_lines, relevant_lines - len(urls), len(urls)))

        with  Pool(16) as pool:
            pool.starmap(urllib.request.urlretrieve, urls)


if __name__ == "__main__":
    run()
