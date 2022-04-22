import calendar
import enum
import os
from datetime import datetime, timedelta

import pypistats
import pandas as pd

from statdate import StatPeriod, StatDate


class PypiStatType(enum.Enum):

    OVERALL = "overall"
    PYTHON_MAJOR = "python_major"
    PYTHON_MINOR = "python_minor"
    SYSTEM = "system"


class WritePypiStat:
    """
    A class used to collect, filter and save pypi statistics to csv files.

    Attributes
    ----------
    _package : str
        name of the target pypi package
    outdir : str, optional
        path of the directory where the gathered data
        will be saved into csv files (default None)
    merge_stored_data: bool, optional
        flag used to merge actual pypi statistics with previously stored (default True)
    drop_percent_column : bool, optional
        flag used to drop percent column (derived) from pypi statistics (default True)
    drop_total_row : bool, optional
        flag used to drop total row (derived) from pypi statistics (default True)

    Methods
    -------
    get_pypistat(stat_type, start_date=None, end_date=None)
        Returns the specified pypi statistics.

    write_pypistat(stat_type, date_period=None, start_date=None, end_date=None)
        Writes the specified pypi statistics.
    """

    def __init__(self, package, outdir=None):
        """
        Parameters
        ----------
        package : str
            name of the target pypi package
        outdir : str, optional
            path of the directory where the gathered data
            will be saved into csv files (default None)
        """

        self._package = package
        self._outdir = outdir

        self._merge_stored_data = True
        self._drop_percent_column = True
        self._drop_total_row = True

    @property
    def outdir(self):
        return self._outdir

    @outdir.setter
    def outdir(self, outdir):
        self._outdir = outdir

    @property
    def merge_stored_data(self):
        return self._merge_stored_data

    @merge_stored_data.setter
    def merge_stored_data(self, merge_stored_data):
        self._merge_stored_data = bool(merge_stored_data)

    @property
    def drop_percent_column(self):
        return self._drop_percent_column

    @drop_percent_column.setter
    def drop_percent_column(self, drop_percent_column):
        self._drop_percent_column = bool(drop_percent_column)

    @property
    def drop_total_row(self):
        return self._drop_total_row

    @drop_total_row.setter
    def drop_total_row(self, drop_total_row):
        self._drop_total_row = bool(drop_total_row)

    def get_pypistat(self, stat_type, start_date=None, end_date=None):
        """Returns the specified pypi statistics.

        Parameters
        ----------
        stat_type : enum
            type of the statistics
            (overall, python_major, python_minor, system)
        start_date : str, optional
            start date of the statistics, should be in one of the following formats:
                "%Y", for example "2022"
                    which means to be collected from "2022-01-01"
                "%Y-%m", for example "2022-01"
                    which means to be collected from "2022-01-01"
                "%Y-%m-%d", for example "2022-01-01"
                    which means to be collected from "2022-01-01"
                None
                    which means to be collected from the last available date
            default (None)
        end_date : str, optional
            end date of the statistics, should be in one of the following formats:
                "%Y", for example "2022"
                    which means to be collected until "2022-12-31"
                "%Y-%m", for example "2022-12"
                    which means to be collected until "2022-12-31"
                "%Y-%m-%d", for example "2022-12-31"
                    which means to be collected until "2022-12-31"
                None
                    which means to be collected until the actual day
            default (None)

        Returns:
        ----------
        pandas.DataFrame: a pandas.DataFrame contains the gathered statistics
        """

        stat_date = StatDate(start=start_date, end=end_date)
        return self._get_pypistat(PypiStatType(stat_type).value, stat_date)

    def _get_pypistat(self, stat_type, stat_date):
        method = getattr(pypistats, stat_type)
        stats = None
        try:
            stats = method(
                self._package,
                total=True,
                start_date=stat_date.start.strftime("%Y-%m-%d"),
                end_date=stat_date.end.strftime("%Y-%m-%d"),
                format="pandas",
            )
        except ValueError:
            return stats
        except IndexError:
            return stats
        if self.drop_percent_column:
            stats.drop(["percent"], inplace=True, axis=1, errors="ignore")
        stats.set_index("date", inplace=True)
        stats.sort_values(["date", "category"], inplace=True)
        if self.drop_total_row and stats.index[-1] is None:
            stats = stats.head(-1)
        return stats

    def _get_pypistat_by_none(self, stat_type, stat_date):
        stats = []
        stat_file = "pypistat" + "_" + stat_type + ".csv"
        stat = self._get_pypistat(stat_type, stat_date)
        if self.merge_stored_data:
            stat = WritePypiStat._concat_with_stored_pypistat(
                self._get_pypistat(stat_type, stat_date),
                self._get_stored_pypistat(stat_file),
            )
        stats.append(
            {
                "stat": stat,
                "stat_file": stat_file,
            }
        )
        return stats

    def _get_pypistat_by_year(self, stat_type, start_date=None, end_date=None):
        stats = []
        time_delta = end_date - start_date
        years = []
        actual_start_date = start_date
        for i in range(time_delta.days + 1):
            day = start_date + timedelta(days=i)
            stat_file = day.strftime("%Y") + "_" + "pypistat" + "_" + stat_type + ".csv"
            if day.year not in years:
                years.append(day.year)
                year_end = datetime(day.year, 12, 31)
                tmp_end_date = year_end if year_end <= end_date else end_date
                stat_date = StatDate(
                    start=actual_start_date.strftime("%Y-%m-%d"),
                    end=tmp_end_date.strftime("%Y-%m-%d"),
                )
                stat = self._get_pypistat(stat_type, stat_date)
                if self.merge_stored_data:
                    stat = WritePypiStat._concat_with_stored_pypistat(
                        self._get_pypistat(stat_type, stat_date),
                        self._get_stored_pypistat(stat_file),
                    )
                stats.append(
                    {
                        "stat": stat,
                        "stat_file": stat_file,
                    }
                )
                actual_start_date = year_end + timedelta(days=1)
        return stats

    def _get_pypistat_by_month(self, stat_type, start_date=None, end_date=None):
        stats = []
        time_delta = end_date - start_date
        months = []
        actual_start_date = start_date
        for i in range(time_delta.days + 1):
            day = start_date + timedelta(days=i)
            stat_file = (
                day.strftime("%Y-%m") + "_" + "pypistat" + "_" + stat_type + ".csv"
            )
            if day.month not in months:
                months.append(day.month)
                month_end = datetime(
                    day.year, day.month, calendar.monthrange(day.year, day.month)[1]
                )
                tmp_end_date = month_end if month_end <= end_date else end_date
                stat_date = StatDate(
                    start=actual_start_date.strftime("%Y-%m-%d"),
                    end=tmp_end_date.strftime("%Y-%m-%d"),
                )
                stat = self._get_pypistat(stat_type, stat_date)
                if self.merge_stored_data:
                    stat = WritePypiStat._concat_with_stored_pypistat(
                        self._get_pypistat(stat_type, stat_date),
                        self._get_stored_pypistat(stat_file),
                    )
                stats.append(
                    {
                        "stat": stat,
                        "stat_file": stat_file,
                    }
                )
                actual_start_date = month_end + timedelta(days=1)
        return stats

    def _get_pypistat_by_day(self, stat_type, start_date=None, end_date=None):
        stats = []
        time_delta = end_date - start_date
        for i in range(time_delta.days + 1):
            day = start_date + timedelta(days=i)
            stat_file = (
                day.strftime("%Y-%m-%d") + "_" + "pypistat" + "_" + stat_type + ".csv"
            )
            stat_date = StatDate(
                start=day.strftime("%Y-%m-%d"), end=day.strftime("%Y-%m-%d")
            )
            stat = self._get_pypistat(stat_type, stat_date)
            if self.merge_stored_data:
                stat = WritePypiStat._concat_with_stored_pypistat(
                    self._get_pypistat(stat_type, stat_date),
                    self._get_stored_pypistat(stat_file),
                )
            stats.append(
                {
                    "stat": stat,
                    "stat_file": stat_file,
                }
            )
        return stats

    def _get_stored_pypistat(self, stat_file):
        stat = None
        if self.outdir:
            stat_file_path = os.path.join(self.outdir, stat_file)
            if os.path.exists(stat_file_path):
                stat = pd.read_csv(stat_file_path)
                stat.set_index("date", inplace=True)
        return stat

    @staticmethod
    def _concat_with_stored_pypistat(stat, stat_stored):
        if stat is not None:
            from_index = stat.first_valid_index()
            if stat_stored is not None:
                stat_stored.drop(
                    stat_stored.loc[stat_stored.index >= from_index].index, inplace=True
                )
            return pd.concat([stat_stored, stat])
        return None

    def write_pypistat(
        self,
        stat_type,
        date_period=None,
        start_date=None,
        end_date=None,
    ):
        """Writes the specified pypi statistics.

        Parameters
        ----------
        stat_type : enum
            type of the statistics
            (overall, python_major, python_minor, system)
        date_period : enum
            grouping of the statistics
            (day, month, year, None)
            default (None)
        start_date : str, optional
            start date of the statistics, should be in one of the following formats:
                "%Y", for example "2022"
                    which means to be collected from "2022-01-01"
                "%Y-%m", for example "2022-01"
                    which means to be collected from "2022-01-01"
                "%Y-%m-%d", for example "2022-01-01"
                    which means to be collected from "2022-01-01"
                None
                    which means to be collected from the last available date
            default (None)
        end_date : str, optional
            end date of the statistics, should be in one of the following formats:
                "%Y", for example "2022"
                    which means to be collected until "2022-12-31"
                "%Y-%m", for example "2022-12"
                    which means to be collected until "2022-12-31"
                "%Y-%m-%d", for example "2022-12-31"
                    which means to be collected until "2022-12-31"
                None
                    which means to be collected until the actual day
            default (None)
        """
        stat_date = StatDate(
            period=StatPeriod(date_period), start=start_date, end=end_date
        )
        self._write_pypistats(PypiStatType(stat_type).value, stat_date)

    def _write_pypistats(
        self,
        stat_type,
        stat_date,
    ):
        stats = []
        if stat_date.period == StatPeriod.DAY:
            stats += self._get_pypistat_by_day(
                stat_type, stat_date.start, stat_date.end
            )
        elif stat_date.period == StatPeriod.MONTH:
            stats += self._get_pypistat_by_month(
                stat_type, stat_date.start, stat_date.end
            )
        elif stat_date.period == StatPeriod.YEAR:
            stats += self._get_pypistat_by_year(
                stat_type, stat_date.start, stat_date.end
            )
        else:
            stats += self._get_pypistat_by_none(stat_type, stat_date)

        for stat in stats:
            self._write_pypistat(stat["stat"], stat["stat_file"])

    def _write_pypistat(self, stat, stat_file):
        if stat is not None:
            print(stat)
            if self.outdir:
                os.makedirs(self.outdir, exist_ok=True)
                stat.to_csv(
                    os.path.join(self.outdir, stat_file), index=True, encoding="utf-8"
                )
