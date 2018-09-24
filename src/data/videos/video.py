import json
import os

import subprocess

LENGTH_CUTOFF = 15*60*1000  # Nothing longer than 15 minutes TODO make sure the cutoff in the graph is at 15 minutes
SIZE_CUTOFF = 100000000  # Nothing above 100 MB

def get_path(platform="youtube"):
    path = os.environ["DATA_PATH"] + "/raw/videos/%s/" % platform
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