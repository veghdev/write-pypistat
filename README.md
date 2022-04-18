[![CI](https://github.com/veghdev/write-pypistat/workflows/CI/badge.svg?branch=main)](https://github.com/veghdev/write-pypistat/actions/workflows/ci.yml)


# About The Project

write-pypistat makes it easy to collect, filter and save pypi statistics to csv files.

# Installation

write-pypistat requires `pypistats` and `pandas` packages.

```sh
pip install write-pypistat
```

# Usage

```python
from writepypistat import WritePypiStat

package = "ipyvizzu"
outdir = "_stat_veghdev_write-pypistat" # optional
write_pypistat = WritePypiStat(package, outdir)

write_pypistat.drop_percent_column = True
write_pypistat.drop_total_row = True

# stat_type: overall, python_major, python_minor, system
write_pypistat.write_pypistat(stat_type="system")

# date_period: None, month, day
# start_date: 2022 | 2022-01 | 2022-01-01 -> 2022-01-01
# end_date: 2022 | 2022-12 | 2022-12-31 -> 2022-12-31
write_pypistat.write_pypistat(stat_type="overall", date_period="month", start_date="2022-01-01", end_date="2022")
```

# Contributing

We welcome contributions to the project, visit our [contributing guide](https://github.com/veghdev/write-pypistat/blob/main/CONTRIBUTING.md) for further info.

# Contact

Join our Discussions page if you have any questions or comments: [Discussions](https://github.com/veghdev/write-pypistat/discussions)

# License

Copyright © 2022.

Released under the [Apache 2.0 License](https://github.com/veghdev/write-pypistat/blob/main/LICENSE).