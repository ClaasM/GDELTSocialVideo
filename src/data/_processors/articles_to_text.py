import glob
import os

from src.boilerpipe.extract import Extractor
from src.util import load_gzip_html

articles_path = os.environ["DATA_PATH"] + "/raw/GDELT/articles/"
text_path = os.environ["DATA_PATH"] + "/raw/GDELT/articles_text/"


# Create the text dir if it does not exist yet
def run():
    if not os.path.exists(text_path):
        os.makedirs(text_path)

    articles = glob.glob(os.path.join(articles_path, "http*"))
    for file_path in articles:
        html = load_gzip_html(file_path)
        text = Extractor(extractor='ArticleExtractor', html=html).getText()
        with open(os.path.join(text_path, file_path.split("/")[-1]), "w+") as f:
            f.write(text)


if __name__ == "__main__":
    run()
