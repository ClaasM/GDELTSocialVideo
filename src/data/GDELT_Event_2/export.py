import pandas as pd
import glob
import os
from src import util

HEADER = ["GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate", "Actor1Code", "Actor1Name",
          "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode", "Actor1Religion1Code",
          "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code", "Actor2Code",
          "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode", "Actor2EthnicCode", "Actor2Religion1Code",
          "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code", "IsRootEvent",
          "EventCode", "EventBaseCode", "EventRootCode", "QuadClass", "GoldsteinScale", "NumMentions",
          "NumSources", "NumArticles", "AvgTone", "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
          "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
          "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code",
          "Actor2Geo_ADM2Code", "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID", "ActionGeo_Type",
          "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code", "ActionGeo_ADM2Code",
          "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID", "DATEADDED", "SOURCEURL"]


class RowIterator:
    def __init__(self):
        self.file_index = 0
        self.file_iterator = iter(sorted(glob.glob(os.environ["DATA_PATH"] + "/external/GDELT/[0-9]*.export.CSV.zip")))
        self.next_file()

    def next_file(self):
        self.file_index += 1
        self.row_index = 0
        self.row_iterator = pd.read_csv(next(self.file_iterator), compression='zip', header=None,
                                        names=util.GDELT_HEADER, delimiter="\t").iterrows()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.file_index, next(self.row_iterator)
        except StopIteration:
            # next file
            self.next_file()
            return self.file_index, self.row_index, next(self.row_iterator)


def find_row_by_id(id):
    for file_index, row_index, row in RowIterator():
        if row[0] == id:
            return file_index, row_index, row


def for_each_row(function):
    """
    Applies function to every row of every file until function returns false.
    :param function:
    :return:
    """

    def task(file):
        df = pd.read_csv(file, compression='zip', header=None, names=util.GDELT_HEADER, delimiter="\t")
        for index, row in df.iterrows():
            if function(index, row):
                return

    for_each_file(task)


def for_each_file(function):
    """
    Applies function to every file until function returns fale
    :param function:
    :return:
    """
    files = glob.glob(os.environ["DATA_PATH"] + "/external/GDELT/[0-9]*.export.CSV.zip")
    for file in files:
        if function(file):
            return


def get_file_path(year=2018, month=7, day=3, hour=15, quarter=0):
    """

    :param year:
    :param month:
    :param day:
    :param hour:
    :param quarter:
    :return:
    """
    return "%s/external/GDELT/%04d%02d%02d%02d%02d00.export.CSV.zip" % (
        os.environ["DATA_PATH"], year, month, day, hour, quarter * 15)
