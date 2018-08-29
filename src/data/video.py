import os
from pytube import YouTube

raw_path = os.environ["DATA_PATH"] + "/raw/videos/"


def download_and_save(url, filename):
    """
    Downloads a video if it does not exist
    :param url: youtube-URL of the video
    :param filename: Name of the file
    :return:
    """

    if os.path.isfile(raw_path + filename):
        return "Already exists"
    else:
        try:
            YouTube(url) \
                .streams \
                .filter(progressive=True, file_extension='mp4') \
                .order_by('resolution') \
                .asc() \
                .first() \
                .download(output_path=raw_path, filename=filename)
            return "Success"
        except Exception as e:
            return str(e)
