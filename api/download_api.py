import urllib


def extract_video(url):
    """

    :param url: the URL of the webpage the video is on
    :return: the video(s) on the page, also follows
    """

"""
Requests the info if not present in the folder and saves it to a file

"""
def get_info(url):
    url = 'https://getvideo.p.mashape.com/' + urllib.parse.urlencode({"url": document_identifier})
    print(url)
    req = urllib.request.Request(url)
    req.add_header('X-Mashape-Key', os.environ["MASHAPE_KEY"])
    response = urllib.request.urlopen(req).read()
    print(response)


"""
Downloads the video if not present in the folder and saves it to a file

"""
def download_video(url, filename):
