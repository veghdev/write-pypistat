import calendar
import enum
import os
from datetime import datetime, timedelta

import pypistats
import pandas as pd
import numpy as np

from .statdate import StatPeriod, StatDate


class PypiStatType(enum.Enum):
    """
    A class used to store the types of pypi statistics
    """

    OVERALL = "overall"
    PYTHON_MAJOR = "python_major"
    PYTHON_MINOR = "python_minor"
    SYSTEM = "system"


class WritePypiStat:
    """
    A class used to collect, filter and save pypi statistics to csv files
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, package_name, outdir=None):
        """
        Constructor of the WritePypiStat class

        Parameters
        ----------
        package_name : str
            name of the target pypi package
        outdir : Union[str, NoneType], default None
            path of the directory where the gathered data
            will be saved into csv files
        """

        self._package_name = package_name
        self._outdir = outdir

        self._date_period = StatPeriod.YEAR

        self._write_package_name = False
        self._merge_stored_data = True
        self._fill_no_data = True
        self._drop_percent_column = True
        self._drop_total_row = True

    @property
    def outdir(self):
        """
        Property used to set outdir

        Parameters
        ----------
        outdir : Union[str, NoneType], default None
            path of the directory where the gathered data
            will be saved into csv files
        """
        return self._outdir

    @outdir.setter
    def outdir(self, outdir):
        self._outdir = outdir

    @property
    def date_period(self):
        """
        Property used to set date_period

        Parameters
        ----------
        date_period : StatPeriod, default StatPeriod.YEAR
            grouping of the statistics
        """
        return self._date_period

    @date_period.setter
    def date_period(self, date_period):
        self._date_period = StatPeriod(date_period)

    @property
    def write_package_name(self):
        """
        Property used to set write_package_name

        Parameters
        ----------
        write_package_name : bool, default False
            flag used to write the name of the package into a csv column
        """
        return self._write_package_name

    @write_package_name.setter
    def write_package_name(self, write_package_name):
        self._write_package_name = bool(write_package_name)

    @property
    def merge_stored_data(self):
        """
        Property used to set merge_stored_data

        Parameters
        ----------
        merge_stored_data : bool, default True
            flag used to merge actual pypi statistics with previously stored
        """
        return self._merge_stored_data

    @merge_stored_data.setter
    def merge_stored_data(self, merge_stored_data):
        self._merge_stored_data = bool(merge_stored_data)

    @property
    def fill_no_data(self):
        """
        Property used to set fill_no_data

        Parameters
        ----------
        fill_no_data : bool, default True
            flag used to create empty lines with 0 download when data is not available
        """
        return self._fill_no_data

    @fill_no_data.setter
    def fill_no_data(self, fill_no_data):
        self._fill_no_data = bool(fill_no_data)

    @property
    def drop_percent_column(self):
        """
        Property used to set drop_percent_column

        Parameters
        ----------
        drop_percent_column : bool, default True
            flag used to drop percent column from pypi statistics
        """
        return self._drop_percent_column

    @drop_percent_column.setter
    def drop_percent_column(self, drop_percent_column):
        self._drop_percent_column = bool(drop_percent_column)

    @property
    def drop_total_row(self):
        """
        Property used to set drop_total_row

        Parameters
        ----------
        drop_total_row : bool, default True
            flag used to drop total row from pypi statistics
        """
        return self._drop_total_row

    @drop_total_row.setter
    def drop_total_row(self, drop_total_row):
        self._drop_total_row = bool(drop_total_row)

    def get_pypistat(self, stat_type, start_date=None, end_date=None):
        """Returns the specified pypi statistics

        Parameters
        ----------
        stat_type : PypiStatType
            type of the statistics
        start_date : Union[str, NoneType], default None
            start date of the statistics, should be in one of the following formats:

            - %Y, for example 2022
                will be 2022-01-01

            - %Y-%m, for example 2022-01
                will be 2022-01-01

            - %Y-%m-%d, for example 2022-01-01
                will be 2022-01-01

            - None
                will be the last available date
        end_date : Union[str, NoneType], default None
            end date of the statistics, should be in one of the following formats:
                - %Y, for example 2022
                    will be 2022-12-31

                - %Y-%m, for example 2022-12
                    will be 2022-12-31

                - %Y-%m-%d, for example 2022-12-31
                    will be 2022-12-31

                - None
                    will be the actual date

        Returns
        -------
        pandas.DataFrame
            the gathered pypi statistics
        """

        stat_date = StatDate(start=start_date, end=end_date)
        return self._get_pypistat(PypiStatType(stat_type).value, stat_date)

    def _get_pypistat(self, stat_type, stat_date):
        method = getattr(pypistats, stat_type)
        stats = None
        try:
            stats = method(
                self._package_name,
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
        stats.sort_values(["date", "category"], inplace=True)
        if self.drop_total_row and stats.iloc[-1]["date"] is None:
            stats = stats.head(-1)
        if self.write_package_name:
            stats.insert(0, "package", self._package_name)
        date_index = stats.pop("date")
        stats.insert(0, date_index.name, date_index)
        stats = WritePypiStat._set_data_frame_columns(stats)
        return stats

    def _get_pypistat_by_none(self, stat_type, stat_date, postfix=None):
        stats = []
        stat_file = postfix if postfix is not None else "pypistat" + "_" + stat_type
        stat_file += ".csv"
        stat = self._get_pypistat(stat_type, stat_date)
        if self.merge_stored_data:
            stat = WritePypiStat._concat_with_stored_pypistat(
                stat,
                self._get_stored_pypistat(stat_file),
                ["date", "package", "category"]
                if self.write_package_name
                else ["date", "category"],
            )
        if self.fill_no_data:
            stat = self._concat_with_no_data(stat, stat_date)
        stats.append({"stat": stat, "stat_file": stat_file})
        return stats

    def _get_pypistat_by_year(
        self, stat_type, start_date=None, end_date=None, postfix=None
    ):
        stats = []
        time_delta = end_date - start_date
        tmp = {
            "years": [],
            "actual_start_date": start_date,
            "actual_year_end": None,
            "actual_end_date": None,
        }
        for i in range(time_delta.days + 1):
            day = start_date + timedelta(days=i)
            stat_file = day.strftime("%Y") + "_"
            stat_file += (
                postfix if postfix is not None else "pypistat" + "_" + stat_type
            )
            stat_file += ".csv"
            if day.year not in tmp["years"]:
                tmp["years"].append(day.year)
                tmp["actual_year_end"] = datetime(day.year, 12, 31)
                tmp["actual_end_date"] = (
                    tmp["actual_year_end"]
                    if tmp["actual_year_end"] <= end_date
                    else end_date
                )
                stat_date = StatDate(
                    start=tmp["actual_start_date"].strftime("%Y-%m-%d"),
                    end=tmp["actual_end_date"].strftime("%Y-%m-%d"),
                )
                stat = self._get_pypistat(stat_type, stat_date)
                if self.merge_stored_data:
                    stat = WritePypiStat._concat_with_stored_pypistat(
                        stat,
                        self._get_stored_pypistat(stat_file),
                        ["date", "package", "category"]
                        if self.write_package_name
                        else ["date", "category"],
                    )
                if self.fill_no_data:
                    stat = self._concat_with_no_data(stat, stat_date)
                stats.append({"stat": stat, "stat_file": stat_file})
                tmp["actual_start_date"] = tmp["actual_year_end"] + timedelta(days=1)
        return stats

    def _get_pypistat_by_month(
        self, stat_type, start_date=None, end_date=None, postfix=None
    ):
        stats = []
        time_delta = end_date - start_date
        tmp = {
            "months": [],
            "actual_start_date": start_date,
            "actual_month_end": None,
            "actual_end_date": None,
        }
        for i in range(time_delta.days + 1):
            day = start_date + timedelta(days=i)
            stat_file = day.strftime("%Y-%m") + "_"
            stat_file += (
                postfix if postfix is not None else "pypistat" + "_" + stat_type
            )
            stat_file += ".csv"
            if day.month not in tmp["months"]:
                tmp["months"].append(day.month)
                tmp["actual_month_end"] = datetime(
                    day.year, day.month, calendar.monthrange(day.year, day.month)[1]
                )
                tmp["actual_end_date"] = (
                    tmp["actual_month_end"]
                    if tmp["actual_month_end"] <= end_date
                    else end_date
                )
                stat_date = StatDate(
                    start=tmp["actual_start_date"].strftime("%Y-%m-%d"),
                    end=tmp["actual_end_date"].strftime("%Y-%m-%d"),
                )
                stat = self._get_pypistat(stat_type, stat_date)
                if self.merge_stored_data:
                    stat = WritePypiStat._concat_with_stored_pypistat(
                        stat,
                        self._get_stored_pypistat(stat_file),
                        ["date", "package", "category"]
                        if self.write_package_name
                        else ["date", "category"],
                    )
                if self.fill_no_data:
                    stat = self._concat_with_no_data(stat, stat_date)
                stats.append(
                    {
                        "stat": stat,
                        "stat_file": stat_file,
                    }
                )
                tmp["actual_start_date"] = tmp["actual_month_end"] + timedelta(days=1)
        return stats

    def _get_pypistat_by_day(
        self, stat_type, start_date=None, end_date=None, postfix=None
    ):
        stats = []
        time_delta = end_date - start_date
        for i in range(time_delta.days + 1):
            day = start_date + timedelta(days=i)
            stat_file = day.strftime("%Y-%m-%d") + "_"
            stat_file += (
                postfix if postfix is not None else "pypistat" + "_" + stat_type
            )
            stat_file += ".csv"
            stat_date = StatDate(
                start=day.strftime("%Y-%m-%d"), end=day.strftime("%Y-%m-%d")
            )
            stat = self._get_pypistat(stat_type, stat_date)
            if self.merge_stored_data:
                stat = WritePypiStat._concat_with_stored_pypistat(
                    stat,
                    self._get_stored_pypistat(stat_file),
                    ["date", "package", "category"]
                    if self.write_package_name
                    else ["date", "category"],
                )
            if self.fill_no_data:
                stat = self._concat_with_no_data(stat, stat_date)
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
                stat = pd.read_csv(
                    stat_file_path, dtype={"downloads": int, "category": str}
                )
                stat = WritePypiStat._set_data_frame_columns(stat)
        return stat

    @staticmethod
    def _concat_with_stored_pypistat(stat, stat_stored, keys):

        if stat is None:
            return stat_stored
        if stat_stored is None:
            return stat

        stat = WritePypiStat._merge_data_frames(stat, stat_stored, keys)

        return stat

    @staticmethod
    def _get_days(stat_date):
        days = []
        time_delta = stat_date.end - stat_date.start
        for i in range(time_delta.days + 1):
            day = stat_date.start + timedelta(days=i)
            days.append(day.strftime("%Y-%m-%d"))
        return days

    def _concat_with_no_data(self, stat, stat_date):
        days = WritePypiStat._get_days(stat_date)

        no_data = {
            "date": days,
            "package": self._package_name,
            "category": np.nan,
            "downloads": 0,
        }

        if not self.write_package_name:
            del no_data["package"]

        if stat is not None:
            del no_data["category"]
            no_data = pd.DataFrame(data=no_data)
            no_data = WritePypiStat._merge_data_frames(
                stat,
                no_data,
                ["date", "package"] if self.write_package_name else ["date"],
            )
        else:
            no_data = pd.DataFrame(data=no_data)
            no_data = WritePypiStat._set_data_frame_columns(no_data)

        return no_data

    @staticmethod
    def _merge_data_frames(dataf1, dataf2, keys):
        dataf1 = dataf1.replace("null", np.nan)
        dataf1 = dataf1.replace("nan", np.nan)
        dataf2 = dataf2.replace("null", np.nan)
        dataf2 = dataf2.replace("nan", np.nan)
        merged = pd.merge(dataf1, dataf2, how="outer", on=[*keys])
        merged.sort_values([*keys], inplace=True)
        if "downloads_y" in merged.columns:
            merged.rename(columns={"downloads_x": "downloads"}, inplace=True)
            merged.rename(columns={"downloads_y": "downloads_x"}, inplace=True)
        merged.downloads.fillna(merged.downloads_x, inplace=True)
        merged.drop(["downloads_x"], inplace=True, axis=1, errors="ignore")
        return merged

    @staticmethod
    def _set_data_frame_columns(dataf):
        for col in dataf.columns:
            if col != "downloads":
                dataf[col] = dataf[col].astype(str)
            else:
                dataf[col] = dataf[col].astype(int)
        return dataf

    @staticmethod
    def _filter_data_frame_rows(stat):
        stat = WritePypiStat._set_data_frame_columns(stat)
        stat = stat.drop_duplicates()
        df_zero = stat[stat["downloads"] == 0]
        df_no_zero = stat[stat["downloads"] != 0]
        stat = stat.drop(df_zero.index[df_zero["date"].isin(df_no_zero["date"])])
        return stat

    def write_pypistat(
        self,
        stat_type,
        start_date=None,
        end_date=None,
        postfix=None,
    ):
        """Writes the specified pypi statistics

        Parameters
        ----------
        stat_type : PypiStatType
            type of the statistics
        start_date : Union[str, NoneType], default None
            start date of the statistics, should be in one of the following formats:

            - %Y, for example 2022
                will be 2022-01-01

            - %Y-%m, for example 2022-01
                will be 2022-01-01

            - %Y-%m-%d, for example 2022-01-01
                will be 2022-01-01

            - None
                will be the last available date
        end_date : Union[str, NoneType], default None
            end date of the statistics, should be in one of the following formats:
                - %Y, for example 2022
                    will be 2022-12-31

                - %Y-%m, for example 2022-12
                    will be 2022-12-31

                - %Y-%m-%d, for example 2022-12-31
                    will be 2022-12-31

                - None
                    will be the actual date
        postfix : str, optional
            postfix of the csv file
        """
        stat_date = StatDate(start=start_date, end=end_date)
        self._write_pypistats(PypiStatType(stat_type).value, stat_date, postfix)

    def _write_pypistats(
        self,
        stat_type,
        stat_date,
        postfix,
    ):
        stats = []
        if self.date_period == StatPeriod.DAY:
            stats += self._get_pypistat_by_day(
                stat_type, stat_date.start, stat_date.end, postfix
            )
        elif self.date_period == StatPeriod.MONTH:
            stats += self._get_pypistat_by_month(
                stat_type, stat_date.start, stat_date.end, postfix
            )
        elif self.date_period == StatPeriod.YEAR:
            stats += self._get_pypistat_by_year(
                stat_type, stat_date.start, stat_date.end, postfix
            )
        else:
            stats += self._get_pypistat_by_none(stat_type, stat_date, postfix)

        for stat in stats:
            self._write_csv(stat["stat"], stat["stat_file"])

    def _write_csv(self, stat, stat_file):
        if stat is not None:
            if self.outdir:
                os.makedirs(self.outdir, exist_ok=True)
                stat = WritePypiStat._filter_data_frame_rows(stat)
                stat.to_csv(
                    os.path.join(self.outdir, stat_file), index=False, encoding="utf-8"
                )
