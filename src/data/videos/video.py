import os

import re
from pytube import YouTube

"""
TODO maybe it makes more sense to move this to util.video
"""


def get_id_from_yt_url(url):
    """
    Not failsafe (its not supposed to be)
    :param url:
    :return:
    """
    # https://www.youtube.com/embed/ZdLMtnNkHvQ?rel=0
    # https://www.youtube.com/embed/ZdLMtnNkHvQ/?rel=0
    # https://www.youtube.com/embed/v=Z2iuL__9a-U?rel=0
    # //www.youtube.com/embed/?wmode=opaque&hd=1&autoplay=0&showinfo=0&controls=0&rel=0
    # https://www.youtube.com/embed//oTyhk1lgZDg?wmode=transparent&start=0
    should_be_id = re.split("/embed[/]+", url)[-1].split("/")[0].split("?")[0]
    occurrences = re.findall("[A-Za-z0-9_-]{11}", should_be_id)
    if len(occurrences) == 1:
        return occurrences[0]
    else:
        raise ValueError("Invalid URL: %s" % url)
