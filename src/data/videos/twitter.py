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

from src.data.videos import video as video_helper

reply_count_selector = "div.permalink-tweet-container div.ProfileTweet-action--reply span.ProfileTweet-actionCountForPresentation"
retweets_count_selector = "div.permalink-tweet-container div.ProfileTweet-action--retweet span.ProfileTweet-actionCountForPresentation"
favorite_count_selector = "div.permalink-tweet-container div.ProfileTweet-action--favorite span.ProfileTweet-actionCountForPresentation"


def download(tweet_id, resolution="lowest_res"):
    """

    :param tweet_id:
    :param resolution:
    :return: Status, View Count, Duraton (ms), Comments (=reply), Shares (=retweets), Likes (=favorite)
    """
    # try:
    video_path = video_helper.get_path("twitter",
                                       resolution)  # TODO If it turns out lowest_res is sufficient, get rid of it altogether

    # Get an Authorization Token by extracting it from the Twitter source code
    video_player_url = 'https://twitter.com/i/videos/tweet/' + tweet_id
    video_player_response = requests.get(video_player_url)
    video_player_soup = BeautifulSoup(video_player_response.text, 'lxml')
    js_file_url = video_player_soup.find('script')['src']
    js_file_response = requests.get(js_file_url)
    bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
    bearer_token = bearer_token_pattern.search(js_file_response.text)
    bearer_token = bearer_token.group(0)

    print(js_file_url)
    print(bearer_token)

    # Talk to the API to get the m3u8 URL using the token just extracted
    player_config_url = 'https://api.twitter.com/1.1/videos/tweet/config/%s.json' % tweet_id
    player_config_response = requests.get(player_config_url, headers={'Authorization': bearer_token})
    player_config = json.loads(player_config_response.text)

    print(player_config)

    if "errors" in player_config:
        return player_config["errors"][0]["message"], 0, 0, 0, 0, 0
    else:
        m3u8_url = player_config['track']['playbackUrl']
        view_count = player_config['track']['viewCount']
        duration = int(player_config['track']['durationMs'])

        # Get some more information by extracting it from the website embedding the tweet
        status_url = "http://twitter.com/i/status/" + tweet_id
        status_response = requests.get(status_url)
        status_soup = BeautifulSoup(status_response.text, 'lxml')
        print(status_soup.text)
        comments = status_soup.find(reply_count_selector)
        shares = status_soup.find(retweets_count_selector)
        likes = status_soup.find(favorite_count_selector)

        print(comments, shares, likes)

        # Get m3u8
        m3u8_response = requests.get(m3u8_url, headers={'Authorization': bearer_token})
        m3u8_url_parse = urllib.parse.urlparse(m3u8_url)
        video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname
        m3u8_parse = m3u8.loads(m3u8_response.text)

        if m3u8_parse.is_variant:
            lowest_res = sorted(m3u8_parse.playlists, key=lambda video: video.stream_info.resolution[0])[0]

            ts_m3u8_response = requests.get(video_host + lowest_res.uri)
            ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

            with open(os.path.join(video_path, tweet_id), 'ab+') as wfd:
                for ts_uri in ts_m3u8_parse.segments.uri:
                    ts_file = requests.get(video_host + ts_uri)
                    wfd.write(ts_file.content)

            return "Success"
        return "Not is_variant"


# except Exception as e:
#		print(e)
#		return str(e)




tweet_with_video = "1041730759613046787"
tweet_with_video_and_audio = "1041782784782589952"
tweet_without_video = "1014956568129892352"

platform = "twitter"
resolution = "lowest_res"

if __name__ == '__main__':
    download(tweet_with_video)
