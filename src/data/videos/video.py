import os
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
    #//www.youtube.com/embed/?wmode=opaque&hd=1&autoplay=0&showinfo=0&controls=0&rel=0
    return url.split('/')[-1].split('?')[0]


