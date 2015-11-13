# -*- coding: utf-8 -*-

"""Ticker Module
Generic US futures and futures options chain
"""

__author__ = "Eric Pieuchot"
__date__ = "9 June 2015"

import comex.static as __DEF__
import comex.function.assets as __COM__
import logging as __LOG__

from datetime import date
from enum import Enum

__all__ = ['get_futures_code', 'get_contract_month',
           'get_bbg_ticker', 'OptType']

#-------------------------------------------------------------------------------
# Generic utility functions
#-------------------------------------------------------------------------------

class OptType(Enum):
    '''Enum type for option type'''
    Unknow, F, C, P = 0, 1, 2, 3

    @staticmethod
    def get(optionType):
        '''Get OptType from string'''
        _opttype = OptType.Unknow
        # Sample function input dictionary
        _dictypes = {'forward':OptType.F, 'f':OptType.F,
                     'call':OptType.C, 'c':OptType.C,
                     'put':OptType.P, 'p':OptType.P}
        # Key retrieval
        if type(optionType) == str:
            _type = optionType.lower()
            if _dictypes.has_key(_type):
                _opttype = _dictypes[_type]
        # Output OptType.get
        return _opttype

#-------------------------------------------------------------------------------
# Futures code utility functions
#-------------------------------------------------------------------------------

def get_futures_code(contractMonth,modYear=True):
    """get future" code from contract month"""
    _futcode = None
    # Sample months dictionary
    _dicmonths = {1:"f", 2:"g", 3:"h", 4:"j", 5:"k", 6:"m",
                  7:"n", 8:"q", 9:"u", 10:"v", 11:"x", 12:"z"}
    _mod = date.today().year - (date.today().year % 10)
    # Check input type
    if isinstance(contractMonth, date):
        if modYear:
            _year = str(contractMonth.year - _mod)
        else:
            _year = str(contractMonth.year)
        _month = _dicmonths[contractMonth.month]
        _futcode = _month.upper() + _year
    # Output get_future_code
    return _futcode

def get_contract_month(futuresCode):
    """Get contract month from futures code"""
    _contractmonth = None
    # Sample codes dictionary
    _diccodes = {"f":1, "g":2, "h":3, "j":4, "k":5, "m":6,
                 "n":7, "q":8, "u":9, "v":10, "x":11, "z":12}
    _mod = date.today().year - (date.today().year % 10)
    # Check input type
    _index = len(futuresCode)
    if (type(futuresCode) == str) and (_index > 1) and (_index < 4):
        _month = futuresCode[0].lower()
        if _diccodes.has_key(_month):
            _month = _diccodes[_month]
            _year = int(futuresCode[1:_index]) + _mod
            _contractmonth = date(_year, _month, 1)
    # Output get_contract_month
    return _contractmonth
    
#-------------------------------------------------------------------------------
# Ticker utility functions
#-------------------------------------------------------------------------------

def get_qdl_ticker(assetName, contractMonth, optionStrike=0, optionType=""):
    """Get Quandl ticker for futures"""
    _qdlticker = None
    # Retrieve static data from xml serialization
    _assets = __COM__.Assets()
    if _assets.xml_to_py():
        if _assets.has_key(assetName):
            _asset = _assets[assetName]
            _ticker = _asset.ticker
            if isinstance(_asset, __COM__.Commodity):
                _family = _asset.family
            elif isinstance(_asset, __COM__.Index):
                _family = __DEF__.ComType.Unknown
        else:
            __LOG__.error("Missing asset %s", assetName, exc_info=True)
    else:
        __LOG__.error("Error loading %s", __DEF__.ROOT_PROJECT, exc_info=True)
    del _assets, _asset
    # Output get_qdl_ticker
    _futcode = get_futures_code(contractMonth,False)
    _qdlticker = _ticker + _futcode
    if _qdlticker != None:
        _qdlticker = _qdlticker.upper()
    return _qdlticker

def get_bbg_ticker(assetName, contractMonth, optionStrike=0, optionType="",
                   bbgKey=False):
    """Get Bloomberg ticker for futures, spreads & options"""
    _bbgticker = None
    # Define output type: spread, futures or option
    _isoption, _isspread, _isfutures = False, False, False
    if type(contractMonth) == str:
        if len(contractMonth.split("/")) > 1:
            _isspread = True
    elif type(contractMonth) == date:
        if optionStrike != 0 or optionType != "":
            _isoption = True
        else:
            _isfutures = True
    # Retrieve static data from xml serialization
    _assets = __COM__.Assets()
    if _assets.xml_to_py():
        if _assets.has_key(assetName):
            _asset = _assets[assetName]
            _ticker = _asset.ticker
            if isinstance(_asset, __COM__.Commodity):
                _key = 'Comdty'
                _family = _asset.family
                _factor = _asset.factor
            elif isinstance(_asset, __COM__.Index):
                _key = 'Index'
                _family = __DEF__.ComType.Unknown
                _factor = 1
        else:
            __LOG__.error("Missing asset %s", assetName, exc_info=True)
    else:
        __LOG__.error("Error loading %s", __DEF__.ROOT_PROJECT, exc_info=True)
    del _assets, _asset
    # Select ticker syntax if futures or options
    if _isfutures or _isoption:
        # CBOT/KBOT/CME exception
        if _family == __DEF__.ComType.AGS:
            _ticker += " "
        _futcode = get_futures_code(contractMonth)
        _bbgticker = _ticker + _futcode
        # Select ticker syntax if option
        if _isoption:
            _strike = str(optionStrike * _factor)
            _type = OptType.get(optionType).name
            _bbgticker += _type + " " + _strike
    # Select ticker syntax if spread
    elif _isspread:
        # CBOT/KBOT/CME exception
        if _family == __DEF__.ComType.AGS:
            _ticker += "_"
        _futcodes = contractMonth.split("/")
        _bbgticker = ""
        for _futcode in _futcodes:
            _bbgticker += _ticker + _futcode
    # Output get_bbg_ticker
    if _bbgticker != None:
        _bbgticker = _bbgticker.upper()
        if bbgKey:
            _bbgticker += " " + _key
    return _bbgticker

#-------------------------------------------------------------------------------
# Unit testing
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    _contract = date(2015, 12, 1)
    _code = get_futures_code(_contract)
    print(_code)
    _contract = get_contract_month(_code)
    print(_contract.isoformat())
    _asset = "WTI_NYMEX"
    _ticker = get_bbg_ticker(_asset, _contract)
    print(_ticker)
    _spread = "z5/z6"
    _ticker = get_bbg_ticker(_asset, _spread)
    print(_ticker)
    _strike = 100
    _type = "call"
    _ticker = get_bbg_ticker(_asset, _contract, _strike, _type)
    print(_ticker)