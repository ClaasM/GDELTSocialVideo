# GDELT Articles & Amateur Video Extraction

This project can be used to extract Youtube videos, Facebook videos and Twitter tweets (plus attached videos, if any)
from the articles in the GDELT dataset.
More than a crawler, it also classifies and only downloads those videos which are relevant to the article,
to ensure a high quality dataset.

## Getting Started

### Prerequisites

git clone https://github.com/ClaasM/GDELTSocialVideo.git

pip install -r requirements.txt
### Initialization

psql -U postgres
CREATE DATABASE gdelt_social_video;

cd GDELTSocialVideo

## Running

### Summary

psql -U postgres -d gdelt_social_video -f src/data/init_db.sql

wget  -P data/external "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"

python3 src/data/download_GDELT.py

python3 src/data/populate_db.py

python3 src/data/crawl_articles.py

TODO:
python3 src/features/build_source_features.py
python3 src/models/predict_sources.py
python3 src/data/crawl_videos.py

For a link to a already finished dataset, containing articles and all relevant videos in the articles, scroll down.
You can also find the intermediary results for each step of the data acquisition there.


### Populating the DB

To check the table sizes:

SELECT relname, (relpages * 8) / 1024 AS size_mb FROM pg_class ORDER BY relpages DESC LIMIT 20;

### Crawling Articles

The articles are saved in data/raw/articles + a path that consists of their domain,
split at dots and reversed, followed by the path of the url. The filename is the last part of the path, plus the query parameters to ensure unique identification.
The fragment identifier is ignored as per RFC TODO quote.

Examples:

www.google.com/ is saved as www under com/google/.
https://www.amazon.com/gp/search/ref=sr_hi_4?rh= is saved as ref=sr_hi_4?rh= under com/amazon/search


To get status on the crawling:
SELECT left(crawling_status, 14), count(left(crawling_status, 14)) FROM articles GROUP BY left(crawling_status, 14) ORDER BY count(left(crawling_status, 14)) DESC;

Reset crawling:
UPDATE articles SET crawling_status='Not Crawled' WHERE crawling_status <> 'Not Crawled';
DELETE FROM article_videos
DELETE FROM sources;

**For the source relevancy classifier (see below) to work, you need at least ~1M crawled articles. Otherwise there will not be enough articles/videos per source to classify it.**

### Crawling Videos

To reset:
UPDATE videos SET crawling_status='Not Crawled'

## Source classification

Not all sources (hosts, e.g. [cnn.com](cnn.com)) have videos in their articles that are relevant to the article.
For example, a website might have a "recommended videos"-section, the contents of which are irrelevant to the article.
A classifier was trained on a manually labeled set of sources to filter these out, with an accuracy of >95%.
More information on how that was achieved can be found in my thesis. TODO link

To use the labeled sources, import them from models/thesis_public_labeled_hosts.csv into the labeled_hosts table:

COPY labeled_sources FROM 'labeled_hosts.csv' DELIMITER ',' CSV;


TODO examples how to get articles for a video, etc.
TODO export are acutally the events, they were just called export for

Make sure the Project is in your PYTHONPATH, otherwise the src wont be importable



# Troubleshooting:

The number of columns might change.
Some files are missing in GDELT (these scripts handle that correctly)

Keyerror: format
ffprobe is not returning anything, because it cant work with ~paths when invoked as a subprocess

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

*Part of* Master thesis for TUM informatics, written at Carnegie Mellon University
