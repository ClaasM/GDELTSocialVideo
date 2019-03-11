import glob
import os
import pandas as pd

from src.data.gdelt import export

class RowIterator:
    def __init__(self, collection="export", header=export.HEADER):
        self.header=header
        self.file_index = 0
        self.file_iterator = iter(sorted(
            glob.glob("%s/external/GDELT/%s/[0-9]*.%s.csv.zip" % (os.environ["DATA_PATH"], collection, collection))))
        self.next_file()

    def next_file(self):
        self.file_index += 1
        self.row_index = 0
        self.row_iterator = pd.read_csv(next(self.file_iterator), compression='zip', header=None,
                                        names=self.header, delimiter="\t").iterrows()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.file_index, next(self.row_iterator)
        except StopIteration:
            # next file
            self.next_file()
            return self.file_index, self.row_index, next(self.row_iterator)
