import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "scraptils",
    version = "0.2.0",
    author = "Stefan Marsiske",
    author_email = "s@ctrlc.hu",
    description = ("Scraping and datamangling Utilities"),
    license = "AGPLv3+",
    keywords = "scraping data",
    packages = find_packages(),
    url = "http://packages.python.org/scraptils",
    py_modules=['scraptils' ],
    long_description=read('README.markdown'),
    classifiers = ["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: GNU Affero General Public License v3",
                   "Environment :: Web Environment",
                   ],
)
