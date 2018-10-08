import json
import os

import subprocess

from src.data.videos import facebook
from src.data.videos import twitter
from src.data.videos import youtube

LENGTH_CUTOFF = 15*60*1000  # Nothing longer than 15 minutes TODO make sure the cutoff in the graph is at 15 minutes
SIZE_CUTOFF = 100000000  # Nothing above 100 MB

def get_path(platform="youtube"):
    # don't create folders here, since this is used in threads
    return os.environ["DATA_PATH"] + "/raw/videos/%s/" % platform

def get_ffprobe_json(file):
    command = ["ffprobe",
               "-loglevel", "quiet",
               "-print_format", "json",
               "-show_format",
               "-show_streams",
               file]

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = pipe.communicate()
    return json.loads(out)


def get_id_from_url(url, platform):
    # TODO maybe using subscripts would work here
    if platform == "youtube":
        return  youtube.get_id_from_url(url)
    elif platform == "twitter":
        return twitter.get_id_from_url(url)
    else:  # if platform == "facebook":
        return facebook.get_id_from_url(url)
