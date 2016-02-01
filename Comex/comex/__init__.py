# -*- coding: utf-8 -*-

"""Comex package"""

__author__ = "Eric Pieuchot"
__date__ = "4 Nov 2015"

# Function package interface
from comex.function.tickers import get_qdl_ticker, get_bbg_ticker
from comex.function.expiries import get_front_month, get_expiry_date

# Start trapping errors
import comex.utility.error as __ERR__
__ERR__.start_logging()
