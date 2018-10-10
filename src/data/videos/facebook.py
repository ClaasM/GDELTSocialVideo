"""
Inspired by:
https://github.com/tbhaxor/fbdown
"""

import os
import re
import traceback
import urllib.parse

import requests
from requests import HTTPError

from src.data.videos import video as video_helper


def download(facebook_video_id):
    """

    :param facebook_video_id: Combination of the actual video id and the username, id + "/" + user_name
    :return:
    """
    ret = dict()
    user_name, video_id = facebook_video_id.split("/")
    try:
        video_path = os.path.join(video_helper.get_path("facebook"), user_name)
        url = "https://www.facebook.com/%s/videos/%s" % (user_name, video_id)

        res = requests.get(url, timeout=5, allow_redirects=True)
        if res.status_code == 200:
            # Alternatively, theres also hd_src and both with _no_ratelimit postfix
            # (but if one doesn't exist, neither does)
            mp4_url_occurences = re.findall("sd_src:\"(.*?)\",", res.text)
            if len(mp4_url_occurences) > 0:
                ret["comments"] = int(re.findall("commentcount:([0-9]*),", res.text)[0])
                ret["shares"] = int(re.findall("sharecount:([0-9]*),", res.text)[0])
                ret["likes"] = int(re.findall("likecount:([0-9]*),", res.text)[0])
                view_count = re.findall("viewCount:\"([0-9,]*)\",", res.text)
                # Number of views are not always present
                if len(view_count) == 1:
                    ret["views"] = int(view_count[0].replace(",", ""))
                else:
                    ret["views"] = -1

                r = requests.get(mp4_url_occurences[0], stream=True)
                if not os.path.exists(video_path):
                    # Every user has its own path
                    os.makedirs(video_path)
                video_file = video_path + "/" + video_id + ".mp4"
                with open(video_file, 'wb+') as file:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)

                ffprobe = video_helper.get_ffprobe_json(video_file)
                ret["duration"] = int(float(ffprobe['format']['duration']) * 1000)
                size = int(ffprobe['format']['size'])

                if ret["duration"] <= video_helper.LENGTH_CUTOFF:
                    if size <= video_helper.SIZE_CUTOFF:
                        ret["crawling_status"] = "Success"
                    else:  # File is too big.
                        os.remove(video_file)
                        ret["crawling_status"] = "Too big"
                else:  # Video is too long.
                    os.remove(video_file)
                    ret["crawling_status"] = "Too long"
            else:
                ret["crawling_status"] = "Video not available"
        else:
            ret["crawling_status"] = res.status_code
    except (HTTPError, ConnectionError):
        ret["crawling_status"] = "Invalid URL"
    except Exception as e:
        traceback.print_exc()
        ret["crawling_status"] = str(e)
    return ret


def get_id_from_url(url):
    """

    :param url:
    :return: user_name + "/" + video_id
    """
    parsed = urllib.parse.urlparse(url)
    video_url = urllib.parse.parse_qs(parsed.query)['href'][0]
    parts = video_url.split("/")
    return parts[-4] + "/" + parts[-2]  # Theres a trailing slash, plus we also need the username in this case.


embedding_url = "https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Ftheweeklytv%2Fvideos%2F2142588782656547%2F&show_text=0&width=476"
non_available_url = "https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Fmonica.j.davis.9%2Fvideos%2F10211561611305403%2F&show_text=1&width=267"

if __name__ == '__main__':
    video_id = get_id_from_url(embedding_url)
    video = download(video_id)
    print(video)
