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

from src.data.videos import video as video_helper

length_cuttoff = 3600  # Nothing longer than an hour
size_cutoff = 10000000000  # Nothing above 10 GB

def download(tweet_id):
    """

    :param tweet_id:
    :param resolution:
    :return: dict: crawling_status, view_count, duraton (ms), comments (=reply), shares (=retweets), likes (=favorite)
    """
    ret = dict()

    try:
        video_path = video_helper.get_path("twitter")

        # Get an authorization and a guest Token by extracting it from the Twitter source code
        video_player_url = 'https://twitter.com/i/videos/tweet/' + tweet_id
        video_player_response = requests.get(video_player_url)
        video_player_soup = BeautifulSoup(video_player_response.text, 'lxml')
        js_file_url = video_player_soup.find('script')['src']
        js_file_response = requests.get(js_file_url)
        bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
        bearer_token = bearer_token_pattern.search(js_file_response.text)
        bearer_token = bearer_token.group(0)
        # past x-guest-tokens:
        # TODO figure out how those are generated or how they can be extracted
        # 1042178736261685249
        guest_token = "1042230193807613957"
        # Talk to the API to get the m3u8 URL using the token just extracted
        player_config_url = 'https://api.twitter.com/1.1/videos/tweet/config/%s.json' % tweet_id
        player_config_response = requests.get(player_config_url,
                                              headers={'Authorization': bearer_token, "x-guest-token": guest_token})
        player_config = json.loads(player_config_response.text)

        if "errors" in player_config:
            ret["crawling_status"] = player_config["errors"][0]["message"]
        else:
            m3u8_url = player_config['track']['playbackUrl']
            ret["view_count"] = int(player_config['track']['viewCount'].replace(',',''))
            ret["duration"] = int(player_config['track']['durationMs'])

            # Get some more information by extracting it from the website embedding the tweet
            status_url = "http://twitter.com/i/status/" + tweet_id
            status_response = requests.get(status_url)
            status_soup = BeautifulSoup(status_response.text, 'lxml')

            stats = status_soup.find("div", {'class': "permalink-tweet-container"})
            ret["comments"] = int(stats.find("div", {'class': "ProfileTweet-action--reply"}).find("span", {
                'class': "ProfileTweet-actionCountForPresentation"}).text)
            ret["shares"] = int(stats.find("div", {'class': "ProfileTweet-action--retweet"}).find("span", {
                'class': "ProfileTweet-actionCountForPresentation"}).text)
            ret["likes"] = int(stats.find("div", {'class': "ProfileTweet-action--favorite"}).find("span", {
                'class': "ProfileTweet-actionCountForPresentation"}).text)

            # Get m3u8
            m3u8_response = requests.get(m3u8_url, headers={'Authorization': bearer_token})
            m3u8_url_parse = urllib.parse.urlparse(m3u8_url)
            video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname
            m3u8_parse = m3u8.loads(m3u8_response.text)

            if m3u8_parse.is_variant:
                lowest_res = sorted(m3u8_parse.playlists, key=lambda video: video.stream_info.resolution[0])[0]

                ts_m3u8_response = requests.get(video_host + lowest_res.uri)
                ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

                # TODO convert to mp4
                with open(os.path.join(video_path, tweet_id + ".ts"), 'ab+') as wfd:
                    for ts_uri in ts_m3u8_parse.segments.uri:
                        ts_file = requests.get(video_host + ts_uri)
                        wfd.write(ts_file.content)

                ret["crawling_status"] = "Success"
            else:
                ret["crawling_status"] = "Not is_variant"
    except Exception as e:
        print(e)
        ret["crawling_status"] = str(e)
    return ret



def get_id_from_url(url):
    # https://twitter.com/georgrestle/status/1036668593520476160?ref_src=twsrc%5Etfw"
    # TODO implement
    return ""




tweet_with_video = "1041730759613046787"
tweet_with_video_and_audio = "1041782784782589952"
tweet_without_video = "1014956568129892352"

platform = "twitter"
resolution = "lowest_res"

if __name__ == '__main__':
    # TODO test other videos
    # TODO convert youtube and implement facebook to/in this format
    print(download(tweet_with_video))
