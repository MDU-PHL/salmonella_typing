"""
salmonella_typing for MDU
"""
from sys import exit, version_info
from setuptools import setup, find_packages
from os import environ
import logging
import styping

# logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"))

# if version_info <= (3, 0):
#     logging.fatal("Sorry, requires Python 3.x, not Python 2.x\n")
#     exit(1)


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="salmonella_typing",
    version="0.2.0",
    description="Run sistr and apply MDU business logic to deal with edge cases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MDU-PHL/salmonella_typing",
    author="Kristy Horan",
    author_email="kristyhoran15@gmail.com",
    maintainer="Kristy Horan",
    maintainer_email="kristyhoran15@gmail.com",
    python_requires=">=3.7, <4",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    zip_safe=False,
    install_requires=["pandas", "xlsxwriter"],
    test_suite="nose.collector",
    tests_require=["nose", "pytest"],
    entry_points={
        "console_scripts": [
            "stype=styping.stype:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: Implementation :: CPython",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    # package_data={"abritamr": ["templates/*", "db/*", "utils/*", "test/*"]}
)
