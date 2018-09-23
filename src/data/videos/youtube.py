"""
Adaption from
https://github.com/h4ckninja/twitter-video-downloader/blob/master/twitter-video-downloader.py
"""
import json
import os
import re
import traceback
import urllib.parse

import m3u8
import requests
from bs4 import BeautifulSoup
from pytube import YouTube

from src.data.videos import video as video_helper

def download(youtube_video_id):
    ret = dict()

    try:
        video_path = video_helper.get_path("youtube")

        # The ID, extracted from the embedding url, is put into the normal yt-url scheme.
        yt_url = "www.youtube.com/watch?v=%s" % youtube_video_id
        yt = YouTube(yt_url)

        ret["duration"] = yt.length * 1000
        ret["views"] = yt.views
        # TODO get the rest of the variables

        if int(yt.length) <= video_helper.LENGTH_CUTOFF:
            stream = yt.streams \
                .filter(progressive=True, file_extension='mp4') \
                .order_by('resolution') \
                .asc() \
                .first()
            if stream.filesize <= video_helper.SIZE_CUTOFF:
                stream.download(output_path=video_path, filename=youtube_video_id)
                ret["crawling_status"] = "Success"
            else:
                ret["crawling_status"] = "Too big"
        else:
            ret["crawling_status"] = "Too long"
    except Exception as e:
        traceback.print_exc()
        ret["crawling_status"] = str(e)
    return ret


def get_id_from_url(url):
    """
    :param url:
    :return:
    """
    should_be_id = re.split("/embed[/]+", url)[-1].split("/")[0].split("?")[0]
    return re.findall("[A-Za-z0-9_-]{11}", should_be_id)[0]


video_id = "bDCHqWpIWd8"

if __name__ == '__main__':
    download(video_id)
