"""
Inspired by:
https://github.com/tbhaxor/fbdown
"""

import os
import re
import urllib.parse

import time
from tqdm import tqdm
import requests
from requests import HTTPError

from src.data.videos import video as video_helper

length_cuttoff = 3600  # Nothing longer than an hour
size_cutoff = 10000000000  # Nothing above 10 GB


def download(facebook_video_id):
    ret = dict()

    try:
        video_path = video_helper.get_path("facebook")

        url = "https://www.facebook.com/theweeklytv/videos/" + facebook_video_id

        res = requests.get(url, timeout=5, allow_redirects=True)
        if res.status_code != 200:
            ret["crawling_status"] = res.status_code
        else:
            ret["comments"] = int(re.findall("commentcount:([0-9]*),", res.text)[0])
            ret["shares"] = int(re.findall("sharecount:([0-9]*),", res.text)[0])
            ret["likes"] = int(re.findall("likecount:([0-9]*),", res.text)[0])
            ret["views"] = int(re.findall("viewCount:\"([0-9,]*)\",", res.text)[0].replace(",", ""))
            ret["duration"] = -1  # TODO

            # Alternatively, theres also hd_src and both with _no_ratelimit postfix
            mp4_url = re.findall("sd_src:\"(.*?)\",", res.text)[0]
            print(mp4_url)
            r = requests.get(mp4_url, stream=True)
            with open(os.path.join(video_path, facebook_video_id + ".mp4"), 'wb+') as file:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

            ret["crawling_status"] = "Success"
    except (HTTPError, ConnectionError):
        ret["crawling_status"] = "Invalid URL"
    # except Exception as e:
    #    print(e)
    #    ret["crawling_status"] = str(e)
    return ret


def get_id_from_url(url):
    parsed = urllib.parse.urlparse(url)
    video_url = urllib.parse.parse_qs(parsed.query)['href'][0]
    return video_url.split("/")[-2]  # Theres a trailing slash

embedding_url = "https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Ftheweeklytv%2Fvideos%2F2142588782656547%2F&show_text=0&width=476"

if __name__ == '__main__':
    video_id = get_id_from_url(embedding_url)
    video = download(video_id)
    print(video)
