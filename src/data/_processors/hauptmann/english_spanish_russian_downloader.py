import os
import urllib.request
from multiprocessing import Pool
import src


YEARS = [2016]

def run():
    # Make sure the data directories for the interesting collections exist.
    path = "%s/other/english/" % os.environ["DATA_PATH"] # spanish_russian
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.environ["DATA_PATH"] + "/external/masterfilelist.txt") as master_file_list:
        urls = list()
        malformed_lines = 0
        for line in master_file_list:
            # Example line: 134072 f1c7a45aa0292b0aee2bc5b674841096 http://data.gdeltproject.org/gdeltv2/20180731191500.export.CSV.zip
            # But some files are missing, then the master file just contains http://data.gdeltproject.org/gdeltv2/
            try:
                url = line.rstrip("\n").split(" ")[2]
                file_name = url.split("/")[-1].lower()  # Casing is inconsistent in the data source, we don't want that
                # Correct year and we're interested in it?
                if int(file_name[:4]) in YEARS and "mentions" in file_name:
                    file_path = "%s/%s" % (path, file_name)
                    urls.append((url, file_path))
            except Exception as e:
                malformed_lines += 1  # Some lines just contain http://data.gdeltproject.org/gdeltv2/


        print("%d relevant files, %d malformed..." % (len(urls), malformed_lines))

        urls = urls[:1000]
        with  Pool(16) as pool:
            pool.starmap(urllib.request.urlretrieve, urls)


if __name__ == "__main__":
    run()
