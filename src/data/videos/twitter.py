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

from src.data.videos import video as video_helper
from src import util

length_cuttoff = 3600  # Nothing longer than an hour
size_cutoff = 10000000000  # Nothing above 10 GB


def download(tweet_id):
    """
    :param tweet_id:
    :return: dict: crawling_status, views, duraton (ms), comments (=reply), shares (=retweets), likes (=favorite)
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
        # For now I'm manually getting one by going to https://twitter.com/i/videos/tweet/1041730759613046787
        # And looking at the request headers for the config request.
        # TODO figure out how those are generated or how they can be extracted
        # past x-guest-tokens:
        # 1042178736261685249
        # 1042230193807613957
        # ...
        guest_token = "1049750915719340034"
        # Talk to the API to get the m3u8 URL using the token just extracted
        player_config_url = 'https://api.twitter.com/1.1/videos/tweet/config/%s.json' % tweet_id
        player_config_response = requests.get(player_config_url,
                                              headers={'Authorization': bearer_token, "x-guest-token": guest_token})

        if player_config_response.status_code == 200:
            player_config = json.loads(player_config_response.text)
            if player_config['track']['contentType'] == 'media_entity':

                m3u8_url = player_config['track']['playbackUrl']
                ret["views"] = util.convert_si_to_number(player_config['track']['viewCount'])
                ret["duration"] = int(player_config['track']['durationMs'])

                # Get some more information by extracting it from the website embedding the tweet
                status_url = "http://twitter.com/i/status/" + tweet_id
                status_response = requests.get(status_url)
                status_soup = BeautifulSoup(status_response.text, 'lxml')

                stats = status_soup.find("div", {'class': "permalink-tweet-container"})
                # Sometimes comments are disabled, then this is just 0.
                ret["comments"] = int(stats.find("span", {'class': "ProfileTweet-action--reply"}).find("span", {
                    'class': "ProfileTweet-actionCount"})['data-tweet-stat-count'])
                ret["shares"] = int(stats.find("span", {'class': "ProfileTweet-action--retweet"}).find("span", {
                    'class': "ProfileTweet-actionCount"})['data-tweet-stat-count'])
                ret["likes"] = int(stats.find("span", {'class': "ProfileTweet-action--favorite"}).find("span", {
                    'class': "ProfileTweet-actionCount"})['data-tweet-stat-count'])

                # Get m3u8
                m3u8_response = requests.get(m3u8_url, headers={'Authorization': bearer_token})
                m3u8_url_parse = urllib.parse.urlparse(m3u8_url)
                video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname
                m3u8_parse = m3u8.loads(m3u8_response.text)

                if m3u8_parse.is_variant:


                    # Find video with 480p resolution or higher (or lower if not available)
                    # ...sort by res
                    sorted_by_res = sorted(m3u8_parse.playlists, key=lambda video: video.stream_info.resolution[0])
                    correct_res = None
                    for video in sorted_by_res:
                        if video.stream_info.resolution[0] >= 480:
                            correct_res = video
                            break
                    if correct_res is None:
                        # No video with resolution >= 480p found
                        correct_res = sorted_by_res[-1]

                    ts_m3u8_response = requests.get(video_host + correct_res.uri)
                    ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

                    # TODO convert to mp4
                    video_file = os.path.join(video_path, tweet_id + ".ts")
                    with open(video_file, 'ab+') as wfd:
                        for ts_uri in ts_m3u8_parse.segments.uri:
                            ts_file = requests.get(video_host + ts_uri)
                            wfd.write(ts_file.content)

                    ffprobe = video_helper.get_ffprobe_json(video_file)
                    duration = int(float(ffprobe['format']['duration']) * 1000)
                    size = int(ffprobe['format']['size'])

                    if duration <= video_helper.LENGTH_CUTOFF:
                        if size <= video_helper.SIZE_CUTOFF:
                            ret["crawling_status"] = "Success"
                        else:  # File is too big.
                            os.remove(video_file)
                            ret["crawling_status"] = "Too big"
                    else:  # Video is too long.
                        os.remove(video_file)
                        ret["crawling_status"] = "Too long"
                else:  # No playlists are contained in the response
                    ret["crawling_status"] = "Not is_variant"
            else:  # The playable media is not a video (e.g. its a gif)
                ret["crawling_status"] = "Content Type: %s" % player_config['track']['contentType']
        else:  # The server returned an error message (most times this is a 404, meaning the tweet doesn't have playable media attached)
            ret["crawling_status"] = "Player Config: %d" % player_config_response.status_code

    except Exception as e:
        traceback.print_exc()
        ret["crawling_status"] = str(e)
    return ret


def get_id_from_url(url):
    # https://twitter.com/georgrestle/status/1036668593520476160?ref_src=twsrc%5Etfw"
    return url.split("/")[-1].split("?")[0]


# TODO turn these into test cases
no_video = "https://twitter.com/Ocasio2018/status/1009049756377714688?ref_src=twsrc%5Etfw"
view_count_none = 'https://twitter.com/TriniGoddess__/status/1013867196790067200?ref_src=twsrc%5Etfw'
view_count_k = 'https://twitter.com/itv2/status/1020051221850263553?ref_src=twsrc%5Etfw'
playlist_empty = 'https://twitter.com/MichelleKHOU/status/1014844223537991680?ref_src=twsrc%5Etfw'
comments_not_identified = 'https://twitter.com/MumbaiPolice/status/1022349566140665856?ref_src=twsrc%5Etfw'
comments_disabled = "https://twitter.com/nbcbayarea/status/1017449870846722050?ref_src=twsrc%5Etfw"

if __name__ == '__main__':
    video_id = get_id_from_url(view_count_k)
    print(video_id)
    print(download(video_id))
