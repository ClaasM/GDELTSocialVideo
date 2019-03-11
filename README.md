# GDELT Articles & Amateur Video Extraction

This project can be used to extract Youtube videos, Facebook videos and Twitter tweets (plus attached videos, if any)
from the articles in the GDELT dataset.
More than a crawler, it also classifies and only downloads those videos which are relevant to the article,
to ensure a high quality dataset.

## Getting Started

### Prerequisites

Clone the repository:

`git clone https://github.com/ClaasM/GDELTSocialVideo.git`

Install the dependencies:

`pip install -r requirements.txt`

### Initialization

Create the database with `src/postgres/sql/init_db.sql`.
Populate the articles table with URLs of articles to be crawled.
Where these URLs come from is dependent on the application, for GDELT the code can be found in `src/gdelt`.

## Running

### Case Study: GDELT

If replicating the case study, the following steps need to be taken.

Create the gdelt-specific tables using:

`src/postgres/sql/init_db_gdelt.sql`.

Download the masterfile:

`wget  -P data/external "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"`

Crawl GDELT:

`python3 src/data/crawl_GDELT.py`

The articles table should now be populated with articles to be crawled.

### Crawling Articles

The articles are saved in `data/raw/articles` + a path that consists of their domain, split at dots and reversed, followed by the path of the url. 
The filename is the last part of the path, plus the query parameters to ensure unique identification.
The fragment identifier is ignored.

Examples:

`www.google.com/` is saved as `www` under `com/google/`.

Start the crawling:

`python3 src/data/crawl_articles.py`

### Crawling Videos

Very similar to article crawling.
Start the crawling:

`python3 src/data/crawl_videos.py`

Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
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
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make predictions
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>