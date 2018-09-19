import os

import re
from pytube import YouTube

"""
TODO maybe it makes more sense to move this to util.video
"""


def get_id_from_youtube_url(url):
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


def get_id_from_twitter_url(url):
    # https://twitter.com/georgrestle/status/1036668593520476160?ref_src=twsrc%5Etfw"
    # TODO implement
    return ""


def get_id_from_facebook_url(url):
    # TODO implement
    return ""


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
