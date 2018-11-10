"""
Extracts all english, spanish and russian documents 2010-2018.

"""

import csv
import glob
import os
import zipfile

import src

language_counter = {"spa":0, "rus":0}
ROW_LIMIT = 20000

# Not using pandas to minimize dependencies.

in_files = glob.glob(
    os.path.join(os.environ["DATA_PATH"], "other/spanish_russian/[0-9]*.translation.mentions.csv.zip"))
spanish_out_file = os.path.join(os.environ["DATA_PATH"], "other/spanish_2016_20k.csv")
russian_out_file = os.path.join(os.environ["DATA_PATH"], "other/russian_2016_20k.csv")

count = 0
with open(spanish_out_file, "w+") as spanish_out_fd, open(russian_out_file, "w+") as russian_out_fd:
    spanish_csv_writer = csv.writer(spanish_out_fd)
    russian_csv_writer = csv.writer(russian_out_fd)
    for file in in_files:
        #print(file)
        archive = zipfile.ZipFile(file)
        archived_file = archive.namelist()[0]
        with archive.open(archived_file) as in_fd:
            for line in in_fd:
                # Can't use csv reader here because it doesn't support byte streams
                cells = line.decode("utf-8").split("\t")
                # print(len(cells))
                if "srclc:spa" in cells[-2]:
                    if language_counter["spa"] < ROW_LIMIT:
                        spanish_csv_writer.writerow(cells[:-1]) # cut off '\n' at the end
                    language_counter["spa"] += 1
                elif "srclc:rus" in cells[-2]:
                    if language_counter["rus"] < ROW_LIMIT:
                        russian_csv_writer.writerow(cells[:-1])  # cut off '\n' at the end
                    language_counter["rus"] += 1

print(language_counter)

