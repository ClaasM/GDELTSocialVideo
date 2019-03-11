import time
from datetime import timedelta
from multiprocessing import Value, Manager

# Each column is 20 chars wide, plus the separator
COL_WIDTH = 12
COLUMNS = ["CURRENT", "TOTAL", "PERCENTAGE", "RUNTIME", "RATE", "EXPECTED"]
COL_SEPARATOR = "|"
ROW_SEPARATOR = "-"
TIME_FORMAT = "%H:%M:%S"


class SyncedCrawlingProgress:
    def __init__(self, total_count=1000, update_every=100000):
        # Variables that need to be synced across Threads
        self.count = Value('i', 0)
        self.last_time = Value('d', time.time())
        self.last_count = Value('i', 0)

        self.start_time = time.time()
        self.update_every = update_every
        self.total_count = total_count
        print(self.row_string(COLUMNS))
        print(ROW_SEPARATOR * (len(COLUMNS) * COL_WIDTH + len(COLUMNS) - 1))

    def row_string(self, values):
        string = ""
        for value in values[0:-1]:
            string += str(value).center(COL_WIDTH) + COL_SEPARATOR
        string += str(values[-1]).center(COL_WIDTH)
        return string

    def inc(self, by=1):
        with self.count.get_lock():
            self.count.value += by
            if self.count.value - self.last_count.value >= self.update_every:
                # Print update
                self.print_update()
                # Then update relevant variables
                with self.last_time.get_lock(), self.last_count.get_lock():
                    self.last_count.value = self.count.value
                    self.last_time.value = time.time()

    def print_update(self):
        # Prints current number, total number, percentage, runtime, increase per second, expected remaining runtime
        percentage = self.count.value / self.total_count * 100
        runtime = time.time() - self.start_time
        increases_per_second = (self.count.value - self.last_count.value) / (time.time() - self.last_time.value)
        expected_remaining_runtime = (self.total_count - self.count.value) / increases_per_second

        print(self.row_string([self.count.value,
                               self.total_count,
                               "%02.0d%%" % percentage,
                               self.time_str(runtime),
                               "%.02f" % increases_per_second,
                               self.time_str(expected_remaining_runtime)
                               ]))

    def time_str(self, seconds):
        return '%02d:%02d:%02d' % (seconds / 3600, seconds / 60 % 60, seconds % 60)

    def set_total_count(self, total_count):
        self.total_count = total_count


class TablePrinter:
    # TODO use this in StatusVisualization
    def __init__(self, header=None):
        if header is None:
            header = ["Col 1", "Col 2", "Col 3"]
        print(self.row_string(header))
        print(ROW_SEPARATOR * (len(COLUMNS) * COL_WIDTH + len(COLUMNS) - 1))

    def print_row(self, row=None):
        if row is None:
            row = ["El1", "El2", "El3"]
        print(self.row_string(row))

    def row_string(self, values):
        string = ""
        for value in values[0:-1]:
            string += str(value).center(COL_WIDTH) + COL_SEPARATOR
        string += str(values[-1]).center(COL_WIDTH)
        return string

"""
Used to visualize the progress of crawling and other things that take time.
Very versatile.
"""
class StatusVisualization:
    def __init__(self, total_count=1000, update_every=100000):
        # Variables that need to be synced across Threads
        self.count = 0
        self.last_time = time.time()
        self.last_count = 0

        self.start_time = time.time()
        self.update_every = update_every
        self.total_count = total_count
        print(self.row_string(COLUMNS))
        print(ROW_SEPARATOR * (len(COLUMNS) * COL_WIDTH + len(COLUMNS) - 1))

    def row_string(self, values):
        string = ""
        for value in values[0:-1]:
            string += str(value).center(COL_WIDTH) + COL_SEPARATOR
        string += str(values[-1]).center(COL_WIDTH)
        return string

    def inc(self, by=1):
        self.count += by
        if self.count - self.last_count >= self.update_every:
            # Print update
            self.print_update()
            # Then update relevant variables
            self.last_count = self.count
            self.last_time = time.time()

    def print_update(self):
        # Prints current number, total number, percentage, runtime, increase per second, expected remaining runtime
        percentage = self.count / self.total_count * 100
        runtime = time.time() - self.start_time
        increases_per_second = (self.count - self.last_count) / (time.time() - self.last_time)
        expected_remaining_runtime = (self.total_count - self.count) / increases_per_second

        print(self.row_string([self.count,
                               self.total_count,
                               "%02.0d%%" % percentage,
                               self.time_str(runtime),
                               "%.02f" % increases_per_second,
                               self.time_str(expected_remaining_runtime)
                               ]))

    def time_str(self, seconds):
        return '%02d:%02d:%02d' % (seconds / 3600, seconds / 60 % 60, seconds % 60)

    def set_total_count(self, total_count):
        self.total_count = total_count
