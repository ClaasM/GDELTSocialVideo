import os

import re
from pytube import YouTube

"""
TODO maybe it makes more sense to move this to util.video
"""


def get_path(platform="youtube", resolution="lowest_res"):
    path = os.environ["DATA_PATH"] + "/raw/videos/%s/%s/" % (platform, resolution)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

"""
                if platform == "youtube":
                    video_id = video_helper.get_id_from_youtube_url(video_url)
                elif platform == "twitter":
                    video_id = video_helper.get_id_from_twitter_url(video_url)
                elif platform == "youtube":
                    video_id = video_helper.get_id_from_facebook_url(video_url)
                video_id = ""  # TODO remove this once the functions are implemented
"""
