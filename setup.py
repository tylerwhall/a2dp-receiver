#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "a2dp_receiver",
    version = "1.0",
    author = "Tyler Hall",
    author_email = "tylerwhall@gmail.com",
    license = "GPLv2",
    entry_points = {
        'console_scripts': [
            'a2dp_receiver = a2dp_receiver:main'
        ]
    },
    packages = find_packages(),
)
