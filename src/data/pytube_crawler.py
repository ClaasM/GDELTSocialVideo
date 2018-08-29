from bs4 import BeautifulSoup
import glob
from src import util
from src.data import video

data_dir = "../../data"
files = glob.glob(data_dir + "/raw/articles/[0-9]*")
output_path = data_dir + "/raw/videos/"
for file in files:
    soup = BeautifulSoup(util.load_gzip_pickle(file), features="lxml")
    iframes = soup.findAll("iframe")
    for iframe in iframes:
        if iframe.has_attr("src"):
            src = iframe['src']
            if "youtube.com" in src:
                file_name = file.split("/")[-1]
                video.download_and_save(src, file.split('/')[-1])


# TODO figure out if we're missing any videos and if youtube-dl, or any other downloader, performs better
# TODO multithreading, etc.