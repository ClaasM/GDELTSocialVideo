# GDELT Articles & Amateur Video Extraction

This project can be used to extract Youtube videos, Facebook videos and Twitter tweets (plus attached videos, if any)
from the articles in the GDELT dataset.
More than a crawler, it also classifies and only downloads those videos which are relevant to the article,
to ensure a high quality dataset.


To drop all tables:
DROP TABLE articles, events, mentions, sources, videos CASCADE;


## Getting Started

### Prerequisites

git clone https://github.com/ClaasM/GDELTSocialVideo.git

pip install -r requirements.txt
### Initialization

psql -U postgres
CREATE DATABASE gdelt_social_video;

cd GDELTSocialVideo

psql -U postgres -d gdelt_social_video -f src/data/init_db.sql

wget  -P data/external "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"

python3 src/data/download_GDELT.py

python3 src/data/populate_db.py


### Extracting

For a link to a already finished dataset, containing articles and all relevant videos in the articles, scroll down.
You can also find the intermediary results for each step of the data acquisition there.

**For the source relevancy classifier (see below) to work, you need at least ~1M crawled articles. Otherwise there will not be enough articles/videos per source to classify it.**





## Source classification

Not all sources (hosts, e.g. [cnn.com](cnn.com)) have videos in their articles that are relevant to the article.
For example, a website might have a "recommended videos"-section, the contents of which are irrelevant to the article.
A classifier was trained on a manually labeled set of sources to filter these out, with an accuracy of >95%.
More information on how that was achieved can be found in my thesis. TODO link



TODO examples how to get articles for a video, etc.
TODO export are acutally the events, they were just called export for



Getting started:

ssh claas@vid-gpu1.inf.cs.cmu.edu
source ~/thesis/bin/activate

python3 src/data/_crawlers/website_crawler.py
slurm -i eth0
top
tmux a
psql -U postgres -d thesis


pg_dump -U postgres thesis > data/other/database_backups/dump_20180914
scp claas@vid-gpu1.inf.cs.cmu.edu:~/dump_20180909 data/
psql -U postgres thesis < data/dump_20180909

Stopping, restarting postgres:
pg_ctl -D /usr/local/var/postgres stop
pg_ctl -D /usr/local/var/postgres start

tmux:
[: scrolling with up and down arrows

To test darknet:

./darknet detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights data/dog.jpg


Make sure the following environment variables are set:

export DYLD_LIBRARY_PATH="/usr/local/cuda/lib"

If using PyCharm, they can be added to the default Python run configuration s.t. they're set for every new python script.
There is no run configuration for Jupyter, though, so the notebook server has to be run from a Terminal (which can be a PyCharm-Terminal, though).

Dependencies:

brew install homebrew/cask/chromedriver

Make sure the Project is in your PYTHONPATH, otherwise the src wont be importable

Useful monitoring:
Check internet speed:
curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python -


# Troubleshooting:

The number of columns might change.
Some files are missing in GDELT (these scripts handle that correctly)

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
