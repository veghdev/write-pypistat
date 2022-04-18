# Contributing

# Issues

You can find our open issues in the project's [issue tracker](https://github.com/veghdev/write-pypistat/issues). Please let us know if you find any issues or have any feature requests there.

# Pull requests

A pull request must contain a linked issue, its title should explain the issue or feature shortly and clearly.

# CI check

The `check` make target collects the targets which are run by the `CI` workflow.
The `CI` workflow invokes the `check-format` and the `lint` targets.

```sh
make check
```

## Formatting

The write-pypistat project is formatted with `black`.
Run the `check-format` target to check that the python files are formatted with `black`.

```sh
make check-format
```

`black` can be run with the `format` make target.

```sh
make format
```

## Linter

The `lint` target runs `pylint` over the write-pypistat project.

```sh
make lint
```

# Release

write-pypistat is distributed on pypi.

## Version number

If your changes are ready to release, you should increase the version number in
`setup.py`. The version bump should be in a separated commit.

```sh
git commit -m 'setup.py: version x.y.z' setup.py
```

Tag this commit:

```sh
git tag x.y.z
```

## Changes

New release should be created on [github](https://github.com/veghdev/write-pypistat/releases/new).

**Note:** Release notes are auto-generated from closed pull requests.

## Package

Publishing a new release will automatically trigger the [Release](https://github.com/veghdev/write-pypistat/blob/main/.github/workflows/release.yml) workflow which builds and uploads the write-pypistat package to [pypi](https://pypi.org/project/write-pypistat/).