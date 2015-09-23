# -*- coding: utf-8 -*-

"""Module Setup
Python distribution
"""

from setuptools import setup, find_packages

setup(name="Comex",
      version="1.2",
      description="Commodity exotics",
      long_description = "Market data analysis tool kit",
      platforms=["Windows","Mac"],
      author="Eric Pieuchot",
      author_email="pieeri_abn@yahoo.co.uk",
      url="https://pypi.python.org/pypi/Comex/",
      license="MIT",
      install_requires=["enum34","pandas"],
      packages=find_packages(),
      package_data={'comex':['data/*.ini','data/*.xml','data/*.txt']})