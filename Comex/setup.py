# -*- coding: utf-8 -*-

"""Module Setup
Python distribution
"""

from setuptools import setup, find_packages

setup(name="Comex",
      version="1.4",
      description="Commodity exotics",
      long_description = "Market data analysis tool kit",
      platforms=["Windows","Mac"],
      author="Eric Pieuchot",
      author_email="eric@rubicubix.co.uk",
      url="https://github.com/Rubicubix/Comex",
      license="MIT",
      install_requires=["enum34","pandas","numpy","blpapi","Quandl"],
      packages=find_packages(),
      package_data={'comex':['data/*.ini','data/*.xml','data/*.txt']})