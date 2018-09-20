"""
Adaption from
https://github.com/h4ckninja/twitter-video-downloader/blob/master/twitter-video-downloader.py
"""
import json
import os
import re
import urllib.parse

import m3u8
import requests
from bs4 import BeautifulSoup
from pytube import YouTube

from src.data.videos import video as video_helper

length_cuttoff = 3600  # Nothing longer than an hour
size_cutoff = 10000000000  # Nothing above 10 GB


def download(youtube_video_id):
	ret = dict()

	try:
		video_path = video_helper.get_path("youtube")

		# The ID, extracted from the embedding url, is put into the normal yt-url scheme.
		yt_url = "www.youtube.com/watch?v=%s" % youtube_video_id
		yt = YouTube(yt_url)

		ret["duration"] = yt.length
		ret["views"] = yt.views
		# TODO get the rest of the variables

		if int(yt.length) <= length_cuttoff:
			stream = yt.streams \
				.filter(progressive=True, file_extension='mp4') \
				.order_by('resolution') \
				.asc() \
				.first()
			if stream.filesize <= size_cutoff:
				stream.download(output_path=video_path, filename=youtube_video_id)
				ret["crawling_status"] = "Success"
			else:
				ret["crawling_status"] = "Too big (%d)" % stream.filesize
		else:
			ret["crawling_status"] = "Too long"
	except Exception as e:
		ret["crawling_status"] = str(e)

	return ret


def get_id_from_url(url):
    """
    :param url:
    :return:
    """
    # https://www.youtube.com/embed/ZdLMtnNkHvQ?rel=0
    # https://www.youtube.com/embed/ZdLMtnNkHvQ/?rel=0
    # https://www.youtube.com/embed/v=Z2iuL__9a-U?rel=0
    # //www.youtube.com/embed/?wmode=opaque&hd=1&autoplay=0&showinfo=0&controls=0&rel=0
    # https://www.youtube.com/embed//oTyhk1lgZDg?wmode=transparent&start=0
    try:
        should_be_id = re.split("/embed[/]+", url)[-1].split("/")[0].split("?")[0]
        occurrences = re.findall("[A-Za-z0-9_-]{11}", should_be_id)
        if len(occurrences) == 1:
            return occurrences[0]
        else:
            return "Wrong number of occurrences (%d)" % len(occurrences)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
	download(tweet_with_video,)