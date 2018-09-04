import os
from multiprocessing.dummy import Pool as DummyPool
from collections import Counter
import urllib.request
from src import util


"""
TODO use progress here as well
"""
YEAR = "2018"
MONTH = "07"
COLLECTION = "mentions"  # Choices are export, gkg or mentions. See GDELT docs.

with open(os.environ["DATA_PATH"] + "/external/masterfilelist.txt") as master_file_list:
    def download_if_not_exists(url):
        # They are sometimes called "CSV" instead of "csv", so I'm converting to lowercase.
        file_path = "%s/external/GDELT/%s/%s" \
                    % (os.environ["DATA_PATH"], COLLECTION, util.get_filename_from_url(url).lower())
        if os.path.isfile(file_path):
            return "Already exists"  # If it already exists, we don't need to download again
        try:
            urllib.request.urlretrieve(url, file_path)
            return "Success"
        except Exception as e:
            print(e)
            return str(e)


    urls = list()
    malformed_lines = 0
    for line in master_file_list:
        try:
            url = line.rstrip("\n").split(" ")[2]
            file_name = util.get_filename_from_url(url)
            # Format is YYYMMDDHHmmSS.
            # Fileending sometimes contains CSV, sometimes csv.
            if file_name.startswith(YEAR + MONTH) and file_name.lower().endswith(COLLECTION + ".csv.zip"):
                urls.append(url)
        except Exception as e:
            malformed_lines += 1  # Some lines are "http://data.gdeltproject.org/gdeltv2/"

    print("%d malformed lines, %d urls scheduled for download" % (malformed_lines, len(urls)))

    pool = DummyPool(16)  # using dummypool because the task is IO-bound anyways
    results = list()
    for result in pool.imap(download_if_not_exists, urls):
        results.append(result)
        if len(results) % 100 == 0:
            print(len(results))  # show progress
    pool.close()
    pool.join()

# Print final tally
print(Counter(results))
