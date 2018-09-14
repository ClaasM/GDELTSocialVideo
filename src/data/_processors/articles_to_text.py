# TODO extract the article from res.data using boilerpipe
import glob
import os

from src.util import load_gzip_html
articles_path = os.environ["DATA_PATH"] + "/raw/GDELT/articles/"
text_path = os.environ["DATA_PATH"] + "/raw/GDELT/articles_text/"

# Create the text dir if it does not exist yet
def run():
    if not os.path.exists(text_path):
        os.makedirs(text_path)

    articles = glob.glob(os.path.join(articles_path, "*"))
    for article in map(load_gzip_html, articles):
        print(article)





if __name__ == "__main__":
    run()
