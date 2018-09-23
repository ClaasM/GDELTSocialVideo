import json
import os

import subprocess

LENGTH_CUTOFF = 3600000  # Nothing longer than an hour
SIZE_CUTOFF = 1000000000  # Nothing above 1 GB

def get_path(platform="youtube"):
    path = os.environ["DATA_PATH"] + "/raw/videos/%s/" % (platform)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

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