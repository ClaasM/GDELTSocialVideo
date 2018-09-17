"""
Adaption from
https://github.com/h4ckninja/twitter-video-downloader/blob/master/twitter-video-downloader.py
"""
import os
import shutil

import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import m3u8
from pathlib import Path
import re

from src import util

def download(tweet_id, path):
	video_player_url_prefix = 'https://twitter.com/i/videos/tweet/'

	# Grab the video client HTML
	video_player_url = video_player_url_prefix + tweet_id
	video_player_response = requests.get(video_player_url)

	# Get the JS file with the Bearer token to talk to the API.
	# Twitter really changed things up.
	js_file_soup = BeautifulSoup(video_player_response.text, 'lxml')
	js_file_url = js_file_soup.find('script')['src']
	js_file_response = requests.get(js_file_url)

	# Pull the bearer token out (this way, we're not restricted in API Access)
	bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
	bearer_token = bearer_token_pattern.search(js_file_response.text)
	bearer_token = bearer_token.group(0)

	# Talk to the API to get the m3u8 URL
	player_config = requests.get('https://api.twitter.com/1.1/videos/tweet/config/' + tweet_id + '.json', headers={'Authorization': bearer_token})
	m3u8_url_get = json.loads(player_config.text)
	m3u8_url_get = m3u8_url_get['track']['playbackUrl']

	#print(json.loads(player_config.text))

	# Get m3u8
	m3u8_response = requests.get(m3u8_url_get, headers = {'Authorization': bearer_token})
	m3u8_url_parse = urllib.parse.urlparse(m3u8_url_get)
	video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname
	m3u8_parse = m3u8.loads(m3u8_response.text)

	if m3u8_parse.is_variant:
		lowest_res = sorted(m3u8_parse.playlists, lambda video: video.stream_info.resolution[0])[0]

		ts_m3u8_response = requests.get(video_host + lowest_res.uri)
		ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

		with open(os.path.join(raw_video_path, tweet_id), 'ab+') as wfd:
			for ts_uri in ts_m3u8_parse.segments.uri:
				ts_file = requests.get(video_host + ts_uri)
				wfd.write(ts_file.content)


tweet_with_video = "1041730759613046787"
tweet_with_video_and_audio = "1041782784782589952"
tweet_without_video = "1014956568129892352"

platform = "twitter"
resolution = "lowest_res"
raw_video_path = os.environ["DATA_PATH"] + "/raw/videos/%s/%s/" % (platform, resolution)

if __name__ == '__main__':
	download(tweet_with_video, raw_video_path)