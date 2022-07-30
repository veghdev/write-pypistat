# Contributing

## Issues

You can find our open issues in the project's [issue tracker](https://github.com/veghdev/write-pypistat/issues/). Please let us know if you find any issues or have any feature requests there.

## CI-CD

### Development environment

You can initialize the development environment of write-pypistat with python virtual env.

Run the `dev` make target to set up your environment.

```sh
make dev
```

**Note:** The `dev` make target is going to set up pre-commit and pre-push hooks into your local git repository. Pre-commit hook is going to format the code with `black` and pre-push hook is going to run the CI steps.

Run the `clean` make target to clear your environment.

```sh
make clean
```

### CI

The CI steps check code formatting, run code analyses and check typing.

The `check` make target collects the above tasks. Run the `check` make target to run the CI steps.

```sh
make check
```

#### Formatting

The write-pypistat project is formatted with `black`.

Run the `format` make target to format your code.

```sh
make format
```

Run the `check-format` target to check code formatting.

```sh
make check-format
```

#### Code analyses

The write-pypistat project is analysed with `pylint`.

Run the `lint` make target to run code analyses.

```sh
make lint
```

#### Typing

The write-pypistat project is using type hints.

Run the `check-typing` make target to run check code typing.

```sh
make check-typing
```

### Documentation

Run the `doc` make target to build the documentation.

```sh
make doc
```

The documentation will be published to the gh-pages branch with the `doc` workflow.
Online version can be read at [veghdev.github.io/write-pypistat](https://veghdev.github.io/write-pypistat/index.html).

### Release

write-pypistat is distributed on [pypi](https://pypi.org/project/write-pypistat). **Note:** You need to be an administrator to release the project.

If you want to release write-pypistat follow the steps below.

- You should increase the version number in `setup.py`. The version bump should be in a separated commit.

- Generate the release notes and publish the new release on [Releases](https://github.com/veghdev/write-pypistat/releases).

 **Note:** Publishing a new release will automatically trigger the `release` workflow which builds, checks and uploads the write-pypistat package to [pypi](https://pypi.org/project/write-pypistat).

You can build and check the package before a release with the `release` make target.

```sh
make release
```
