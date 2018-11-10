"""
Extracts all english, spanish and russian documents 2010-2018.

"""

import csv
import glob
import os
import zipfile
import sys

import src

# Not using pandas to minimize dependencies.

in_files = glob.glob(
    os.path.join(os.environ["DATA_PATH"], "other/english/[0-9]*.mentions.csv.zip"))
out_file = os.path.join(os.environ["DATA_PATH"], "other/english_2016_20k.csv")
count = 0
with open(out_file, "w+") as out_fd:
    csv_writer = csv.writer(out_fd)
    for file in in_files:
        #print(file)
        archive = zipfile.ZipFile(file)
        archived_file = archive.namelist()[0]
        with archive.open(archived_file) as in_fd:
            for line in in_fd:
                # Can't use csv reader here because it doesn't support byte streams
                cells = line.decode("utf-8").split("\t")
                # We only want those events that happened in Ukraine or were either party is ukrainian
                # print(len(cells))
                csv_writer.writerow(cells[:-1])
                count += 1
                if count == 20000:
                    sys.exit(0)

print("%d lines written" % count)

