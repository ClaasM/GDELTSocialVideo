import glob
import os
from multiprocessing.pool import Pool

import pandas as pd

from src.visualization.console import CrawlingProgress
from src import constants

crawling_progress = CrawlingProgress(constants.GDELT_MENTIONS_LENGTH)

def count_lines(file):
    file_count = 0
    df = pd.read_csv(file, compression='zip', header=None, names=["GlobalEventID"], delimiter="\t", usecols=[0])
    for _ in df.iterrows():
        crawling_progress.inc(1)
        file_count += 1
    return file_count


def run():

    # Count mentions while showing a progress bar
    pool = Pool(4)
    files = glob.glob(os.environ["DATA_PATH"] + "/external/GDELT/mentions/[0-9]*.mentions.csv.zip")

    count = 0
    for result in pool.imap_unordered(count_lines, files):
        count += result
        # print(result)

    print(count)
    pool.close()
    pool.join()


# Its 17519003
if __name__ == "__main__":
    run()
