#!/usr/bin/env python
from setuptools import find_packages, setup

NAME = "growth"
VERSION = "1.0.0"
AUTHOR = "Arshad Ansari"
EMAIL = "arshadansari27@outlook.com"
DESCRIPTION = "Growth App"
URL = "https://github.com/arshadansari27/growth_board"
REQUIRES_PYTHON = "3.8"

INSTALL_REQUIRES = [str(ir) for ir in open("requirements.txt")]

TESTS_REQUIRE = ["nose", "freezegun==0.1.11"]

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),
    packages_dir={"": "growth"},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    entry_points="""
        [console_scripts]
        growth=growth:cli
    """,
)
