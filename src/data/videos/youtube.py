import os
import re
import traceback

import youtube_dl

from src.data.videos import video as video_helper


class QuietLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def download(youtube_video_id):
    ret = dict()

    try:
        video_path = video_helper.get_path("youtube")
        video_file = video_path + youtube_video_id + ".mp4"
        ydl_opts = {
            # Download smallest file but not less then 240p (so not 144p for example)
            # TODO the alternatives might not be needed since its always available in mp4
            'format': 'worst[height>=240][ext=mp4]/worst[height>=240]/worst',  # best[height<=360][ext=mp4]
            'outtmpl': video_file,
            'quiet': True,
            'logger': QuietLogger(),
            # Make 100% sure everything is mp4 in the end
            # TODO might not be needed
            #'postprocessors': [{
            #    'key': 'FFmpegVideoConvertor',
            #    'preferedformat': 'mp4'
            # }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ret = dict()
            info = ydl.extract_info(youtube_video_id, download=False)

            if "_type" not in info or info["_type"] != "playlist":

                # Likes might be disabled
                ret["likes"] = info["like_count"] if "like_count" in info else -1
                ret["views"] = info["view_count"] if "view_count" in info else -1
                ret["duration"] = info["duration"] * 1000
                # Youtube-dl does not extract these at this point, neither does pytube.
                ret["comments"] = -1
                ret["shares"] = -1

                if ret["duration"] <= video_helper.LENGTH_CUTOFF:
                    # Only download if its not too long
                    ydl.extract_info(youtube_video_id, download=True)
                    ffprobe = video_helper.get_ffprobe_json(video_file)
                    size = int(ffprobe['format']['size'])

                    if size <= video_helper.SIZE_CUTOFF:
                        ret["crawling_status"] = "Success"
                    else:  # File is too big.
                        os.remove(video_file)
                        ret["crawling_status"] = "Too big"
                else:  # Video is too long.
                    ret["crawling_status"] = "Too long"
            else:
                ret["crawling_status"] = "Is stream recording"
    except Exception as e:
        # traceback.print_exc()
        ret["crawling_status"] = str(e)[:100]  # to prevent filling the db with stack traces
    return ret


def get_id_from_url(url):
    """
    :param url:
    :return:
    """
    should_be_id = re.split("/embed[/]+", url)[-1].split("/")[0].split("?")[0]
    return re.findall("[A-Za-z0-9_-]{11}", should_be_id)[0]


example_vid = "bDCHqWpIWd8"

if __name__ == '__main__':
    download(example_vid)
