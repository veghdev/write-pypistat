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

package = "pypistats"
outdir = "stats/pypistat"
write_pypistat = WritePypiStat(package, outdir)

write_pypistat.write_pypistat.write_pypistat(
    stat_type="system",
    start_date="2022",
    end_date="2022-03",
)
```

Visit our [wiki](https://github.com/veghdev/write-pypistat/wiki) site for more details.

# Contributing

We welcome contributions to the project, visit our [contributing](https://github.com/veghdev/write-pypistat/blob/main/CONTRIBUTING.md) guide for further info.

# Contact

Join our [discussions](https://github.com/veghdev/write-pypistat/discussions) page if you have any questions or comments.

# License

Copyright © 2022.

Released under the [Apache 2.0 License](https://github.com/veghdev/write-pypistat/blob/main/LICENSE).
