import calendar
import enum
from datetime import datetime, timedelta


class StatPeriod(enum.Enum):

    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    NONE = None


class StatDate:
    def __init__(self, start=None, end=None):
        self._start = StatDate.format_start(start)
        self._end = StatDate.format_end(end)
        assert self._start <= self._end, "start must be before end"

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        start = StatDate.format_start(start)
        if self.end and start:
            assert start <= self.end, "start must be before end"
        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        end = StatDate.format_end(end)
        if self.start and end:
            assert self.start <= end, "start must be before end"
        self._end = end

    @staticmethod
    def format_start(start):
        time_delta_max = 181
        if start is None:
            time_delta = timedelta(days=time_delta_max)
            start = datetime.now() - time_delta
        if isinstance(start, datetime):
            start = start.strftime("%Y-%m-%d")
        parsed_start = start.split("-")
        if len(parsed_start) == 1:
            start += "-01-01"
        elif len(parsed_start) == 2:
            start += "-01"
        elif len(parsed_start) == 3:
            pass
        else:
            raise ValueError(f"{start} format is incorrect")
        return datetime.strptime(start, "%Y-%m-%d")

    @staticmethod
    def format_end(end):
        if end is None:
            end = datetime.now()
        if isinstance(end, datetime):
            end = end.strftime("%Y-%m-%d")
        parsed_end = end.split("-")
        if len(parsed_end) == 1:
            end += "-12-31"
        elif len(parsed_end) == 2:
            end += "-" + str(
                calendar.monthrange(int(parsed_end[0]), int(parsed_end[1]))[1]
            )
        elif len(parsed_end) == 3:
            pass
        else:
            raise ValueError(f"{end} format is incorrect")
        return datetime.strptime(end, "%Y-%m-%d")
