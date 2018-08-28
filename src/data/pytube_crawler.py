from bs4 import BeautifulSoup
import glob
from pytube import YouTube
from src import util

data_dir = "../../data"
files = glob.glob(data_dir + "/raw/articles/[0-9]*")
output_path = data_dir + "/raw/videos"
for file in files:
    soup = BeautifulSoup(util.load_gzip_pickle(file), features="lxml")
    iframes = soup.findAll("iframe")
    for iframe in iframes:
        if iframe.has_attr("src"):
            src = iframe['src']
            if "youtube.com" in src:
                try:
                    YouTube(iframe['src']) \
                        .streams \
                        .filter(progressive=True, file_extension='mp4') \
                        .order_by('resolution') \
                        .asc() \
                        .first() \
                        .download(filename=file.split("/")[-1], )
                    # ydl.download([iframe['src']], info_filename="../" + path.split("/")[-1])
                except Exception as e:
                    print(e)

# TODO figure out if we're missing any videos and if youtube-dl, or any other downloader, performs better