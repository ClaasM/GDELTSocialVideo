Getting started:

ssh claas@vid-gpu1.inf.cs.cmu.edu
source ~/thesis/bin/activate

python3 src/data/_crawlers/website_crawler.py
slurm -i eth0
top
psql -U postgres -d thesis
pg_dump -U postgres thesis > dump
scp claas@vid-gpu1.inf.cs.cmu.edu:~/dump data/
psql -U postgres thesis < /dump


postgres -D /usr/local/var/postgres/


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


SQLite:

apt install..
sqlite data/interim/GDELT.db
.read src/data/init_db.sql

master_thesis
==============================

Master thesis for TUM informatics, written at Carnegie Mellon University

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

