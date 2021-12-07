# -*- coding: utf-8 -*-
"""Django Zendesk"""

__name__ = "django_zendesk"
__author__ = "Pivotal Energy Solutions"
__version_info__ = (2, 1, 6)
__version__ = "2.1.6"
__date__ = "2014/07/22 4:47:00 PM"
__credits__ = ["Steven Klass", "Tim Valenta"]
__license__ = "See the file LICENSE.txt for licensing information."

from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

name = "pivotal_" + __name__
base_url = "https://github.com/pivotal-energy-solutions/django_zendesk"

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=name,  # Required
    version="2.1.6",  # Required
    description="Provides single-sign on functionality between a django.contrib.auth"
    " based site and Zendesk",  # Required
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url=base_url,  # Optional
    download_url="{0}/archive/{1}.tar.gz".format(base_url, __version__),
    author=__author__,  # Optional
    author_email="steven@pivotalenergysolutions.com",  # Optional
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License (Proprietary)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9.*",
    install_requires=["django>=3.2", "requests"],
    keywords="django zendesk authentication",  # Optional
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    project_urls={  # Optional
        "Bug Reports": "{}/issues".format(base_url),
        "Say Thanks!": "https://saythanks.io/to/rh0dium",
        "Original Source": "https://bitbucket.org/jonknee/django_zendesk",
    },
)
