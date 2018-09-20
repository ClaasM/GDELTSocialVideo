import os

import re
from pytube import YouTube

def get_path(platform="youtube"):
    path = os.environ["DATA_PATH"] + "/raw/videos/%s/" % (platform)
    if not os.path.exists(path):
        os.makedirs(path)
    return path