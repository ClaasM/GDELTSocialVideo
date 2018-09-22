import csv
import glob
import os
import zipfile

import sys

import src

# Not using pandas to minimize dependencies.
in_files = glob.glob(os.path.join(os.environ["DATA_PATH"], "other/mh17/[0-9]*.export.CSV.zip"))
out_file = os.path.join(os.environ["DATA_PATH"], "other/mh17/ukraine_20140717-20140731.csv")
count = 0
with open(out_file, "w+") as out_fd:
    csv_writer = csv.writer(out_fd)
    for file in in_files:
        print(file)
        archive = zipfile.ZipFile(file)
        archived_file = archive.namelist()[0]
        with archive.open(archived_file) as in_fd:
            for line in in_fd:
                # Can't use csv reader here because it doesn't support byte streams
                cells = line.decode("utf-8").split("\t")
                # We only want those events that happened in Ukraine or were either party is ukrainian
                if "Ukraine" in cells[36] or "Ukraine" in cells[43] or "Ukraine" in cells[50]:
                    cells[-1] = cells[-1][:-2] # cut off the \n character at the end of each line
                    csv_writer.writerow(cells)
                    count += 1

print("%d lines written" % count)