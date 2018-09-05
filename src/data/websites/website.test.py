import glob
import os

from lxml import etree

from src.data.websites import website

example_websites = glob.glob(os.environ["DATA_PATH"] + "/examples/websites/*.html")

for site in example_websites:
    print(site)
    tree = etree.parse(site, etree.HTMLParser())
    website.get_video_sources_etree(tree)
