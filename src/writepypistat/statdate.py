import calendar
import enum
from datetime import datetime, timedelta


class StatPeriod(enum.Enum):
    """
    A class used to store the grouping types for the statistics
    """

    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    NONE = None


class StatDate:
    """
    A class used to set and format the dates of the statistics
    """

    def __init__(self, start=None, end=None):
        """
        Constructor of the StatDate class

        Parameters
        ----------
        start : Union[str, NoneType], default None
            start date for pypi statistics
            (None means to be collected from the last available date)
        end : Union[str, NoneType], default None
            end date for pypi statistics
            (None means to be collected until the actual day)
        """

        self._start = StatDate.format_start(start)
        self._end = StatDate.format_end(end)
        assert self._start <= self._end, "start must be before end"

    @property
    def start(self):
        """
        Property used to start

        Parameters
        ----------
        start : Union[str, NoneType], default None
            start date for pypi statistics
            (None means to be collected from the last available date)
        """
        return self._start

    @start.setter
    def start(self, start):
        start = StatDate.format_start(start)
        if self.end and start:
            assert start <= self.end, "start must be before end"
        self._start = start

    @property
    def end(self):
        """
        Property used to end

        Parameters
        ----------
        end : Union[str, NoneType], default None
            end date for pypi statistics
            (None means to be collected until the actual day)
        """
        return self._end

    @end.setter
    def end(self, end):
        end = StatDate.format_end(end)
        if self.start and end:
            assert self.start <= end, "start must be before end"
        self._end = end

    @staticmethod
    def format_start(start):
        """
        Method used to format start date

        - %Y, for example 2022
            will be formatted to 2022-01-01

        - %Y-%m, for example 2022-01
            will be formatted to 2022-01-01

        - %Y-%m-%d, for example 2022-01-01
            will be formatted to 2022-01-01

        - None
            will be formatted to the last available date

        Parameters
        ----------
        start : Union[str, NoneType]
            start date for pypi statistics
        """

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
        """
        Method used to format end date

        - %Y, for example 2022
            will be formatted to 2022-12-31

        - %Y-%m, for example 2022-12
            will be formatted to 2022-12-31

        - %Y-%m-%d, for example 2022-12-31
            will be formatted to 2022-12-31

        - None
            will be formatted to the actual date

        Parameters
        ----------
        end : Union[str, NoneType]
            end date for pypi statistics
        """

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
