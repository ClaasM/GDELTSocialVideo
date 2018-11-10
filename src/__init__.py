import os

# TODO remove
# Local: "/Users/claasmeiners/data/"
# External drive: "/Volumes/DeskDrive/data/"

os.environ["DATA_PATH"] = "/Users/claasmeiners/data/"
os.environ["MODEL_PATH"] = os.path.dirname(os.path.realpath(__file__)) + "/../models/"
os.environ["FIGURES_PATH"] = os.path.dirname(os.path.realpath(__file__)) + "/../reports/figures/"
