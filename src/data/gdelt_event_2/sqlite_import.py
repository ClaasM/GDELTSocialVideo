"""
This script extracts the relevant GDELT data and puts it into the sqlite database.
"""

TABLE_NAME = "gdelt"

columns = ["GLOBALEVENTID", "EventCode", "EventBaseCode", "EventRootCode"]