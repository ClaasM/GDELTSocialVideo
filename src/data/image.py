

def download_and_save(id, url):
    """
    Queues an image for download if it does not exist
    :param id: Name of the file
    :param url: URL of the image
    :return:
    """

    urllib.request.urlretrieve(article.ImageURL, "%s/%s" % (image_path, article.DATE))

    return