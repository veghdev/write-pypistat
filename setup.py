#!/usr/bin/env python3
from setuptools import setup

with open("requirements.txt") as fp:
    requirements = fp.read().splitlines()

with open("README.md") as fp:
    long_description = fp.read()

setup(
    name="write-pypistat",
    version="0.0.0",
    description="Filter and write pypi statistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    py_modules=["writepypistat", "statdate"],
    python_requires=">=3.6",
    install_requires=requirements,
    url="https://github.com/veghdev/write-pypistat",
    project_urls={
        "Documentation": "https://github.com/veghdev/write-pypistat",
        "Source": "https://github.com/veghdev/write-pypistat",
        "Tracker": "https://github.com/veghdev/write-pypistat/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
)