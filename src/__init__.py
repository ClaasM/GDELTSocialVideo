import os

# TODO remove
# Local: "/Users/claasmeiners/data/"
# External drive: "/Volumes/DeskDrive/data/"

if "DATA_PATH" not in os.environ:
    os.environ["DATA_PATH"] = "/mnt/claas/data/"

os.environ["MODEL_PATH"] = "/mnt/claas/models/" # os.path.dirname(os.path.realpath(__file__)) + "/../models/"
os.environ["FIGURES_PATH"] = os.path.dirname(os.path.realpath(__file__)) + "/../reports/figures/"
