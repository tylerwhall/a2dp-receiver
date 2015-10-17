#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name = "a2dp_receiver",
    version = "1.0",
    author = "Tyler Hall",
    author_email = "tylerwhall@gmail.com",
    license = "GPLv2",
    scripts = ['bin/a2dp_receiver'],
    packages = find_packages(),
)
