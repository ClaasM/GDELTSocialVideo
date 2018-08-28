import requests

def download_file(url):
    """
    Source: https://stackoverflow.com/questions/35842873/is-there-a-way-to-download-a-video-from-a-webpage-with-python
    :param url:
    :return:
    """
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

download_file("http://www.jpopsuki.tv/images/media/eec457785fba1b9bb35481f438cf35a7_1351466328.mp4")