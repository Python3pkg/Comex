# -*- coding: utf-8 -*-

"""Expiry Module
Expiry utility package for commodity futures and futures options
"""

__author__ = "Eric Pieuchot"
__date__ = "9 June 2015"

import comex.static as __DEF__
import comex.function.assets as __COM__
import logging as __LOG__

from datetime import date, timedelta
from enum import Enum

__all__ = ['ExpType', 'get_expiry_date', 'get_front_month']

#-------------------------------------------------------------------------------
# Generic utility functions
#-------------------------------------------------------------------------------

class ExpType(Enum):
    '''Enum type for expiry type'''
    Unknow, F, OF, N = 0, 1, 2, 3

    @staticmethod
    def get(expiryType):
        '''Get ExpType from string'''
        _exptype = ExpType.Unknow
        # Sample function input dictionary
        _dictypes = {'futures':ExpType.F, 'f':ExpType.F,
                     'notice':ExpType.N, 'n':ExpType.N,
                     'options':ExpType.OF, 'of':ExpType.OF, 'o':ExpType.OF}
        # Key retrieval
        if type(expiryType) == str:
            _type = expiryType.lower()
            if _dictypes.has_key(_type):
                _exptype = _dictypes[_type]
        # Output ExpType.get
        return _exptype

#-------------------------------------------------------------------------------
# Expiry utility functions
#-------------------------------------------------------------------------------

def get_front_month(assetName, baseDate, expiryType, lag=0):
    """
    Description
    -----------
    Get front month contract for commodity futures
        
    Parameters
    ----------
        assetName (string): Comex asset name
        
        baseDate (date): date object
        
        expiryType (string): futures 'F', notice 'N', options 'OF'
        
        lag (integer): lag roll for expiryType
        
    Examples
    --------
        functionReturn (date)::
            
            >>> comex.get_font_month()
            date()
    """
    _front = None
    # Retrieve static from XML serialization
    _assets = __COM__.Assets()
    if _assets.xml_to_py():
        if _assets.has_key(assetName):
            _asset = _assets[assetName]
            if isinstance(_asset, __COM__.Commodity):
                if isinstance(baseDate, date):
                    _cal = _asset.get_custom_date()
                    baseDate += lag * _cal
                    _roll = date(baseDate.year, baseDate.month, baseDate.day)
                    _front = date(baseDate.year, baseDate.month, 1)
                    while(True):
                        _expiry = get_expiry_date(_asset.name, _front, expiryType)
                        if _expiry < _roll:
                            if _front.month == 12:
                                _front = date(_front.year + 1, 1, 1)
                            else:
                                _front = date(_front.year, _front.month + 1, 1)
                        else:
                            break
                else:
                    __LOG__.error("Type %s", type(baseDate), exc_info=True)
            else:
                __LOG__.error("Instance %s", type(_asset), exc_info=True)
        else:
            __LOG__.error("Missing %s", assetName, exc_info=True)
    else:
        __LOG__.error("Loading %s", __DEF__.ROOT_PROJECT, exc_info=True)
    # Output get_expiry_date
    return _front

def get_expiry_date(assetName, contractMonth, expiryType):
    """
    Description
    -----------
    Get first notice and expiration dates for commodity futures and options
        
    Parameters
    ----------
        assetName (string): Comex asset name
        
        contractMonth (date): date object
        
        expiryType (string): futures 'F', notice 'N', options 'OF'
        
    Examples
    --------
        functionReturn (date)::
            
            >>> comex.get_expiry_date("WTI_NYMEX", date(2015, 12, 1), "F")
            date(2015, 11, 20)
    """
    _expiry = None
    # Retrieve static from XML serialization
    _assets = __COM__.Assets()
    if _assets.xml_to_py():
        if _assets.has_key(assetName):
            _asset = _assets[assetName]
            if isinstance(_asset, __COM__.Commodity):
                if isinstance(contractMonth, date):
                    _type = ExpType.get(expiryType)
                    _cal = _asset.get_custom_date()
                    if assetName == "WTI_NYMEX":
                        _expiry = __wti_nymex_exp__(_cal, contractMonth, _type)
                    elif assetName == "WTI_ICE":
                        _expiry = __wti_ice_exp__(_cal, contractMonth, _type)
                    elif "BR" in assetName:
                        _expiry = __br_ice_exp__(_cal, contractMonth, _type)
                    elif assetName == "HO_NYMEX" or assetName == "RB_NYMEX":
                        _expiry = __ho_nymex_exp__(_cal, contractMonth, _type)
                    elif assetName == "NG_NYMEX":
                        _expiry = __ng_nymex_exp__(_cal, contractMonth, _type)
                    elif assetName == "GO_ICE":
                        _expiry = __go_ice_exp__(_cal, contractMonth, _type)
                else:
                    __LOG__.error("Type %s", type(contractMonth), exc_info=True)
            else:
                __LOG__.error("Instance %s", type(_asset), exc_info=True)
        else:
            __LOG__.error("Missing %s", assetName, exc_info=True)
    else:
        __LOG__.error("Loading %s", __DEF__.ROOT_PROJECT, exc_info=True)
    # Output get_expiry_date
    if _expiry != None:
        _expiry = date(_expiry.year, _expiry.month, _expiry.day)
    return _expiry

#-------------------------------------------------------------------------------
# Energy futures expiries
#-------------------------------------------------------------------------------

def __wti_nymex_exp__(assetCalendar, contractMonth, expiryType):
    """Get expiry dates for WTI NYMEX contracts"""
    _expiry = None
    # Retrieve futures expiry date
    if contractMonth.month == 1:
        _expiry = date(contractMonth.year - 1, 12, 25)
    else:
        _expiry = date(contractMonth.year, contractMonth.month - 1, 25)
    if assetCalendar.onOffset(_expiry):
        _expiry -= 3 * assetCalendar
    else:
        _expiry -= 4 * assetCalendar
    # Retrieve options expiry date
    if expiryType == ExpType.OF:
        _expiry -= 3 * assetCalendar
    # Output __wti_nymex_exp__
    return _expiry

def __ho_nymex_exp__(assetCalendar, contractMonth, expiryType):
    """Get expiry dates for HO & RB NYMEX contracts"""
    _expiry = None
    # Retrieve futures expiry date
    _expiry = date(contractMonth.year, contractMonth.month, 1)
    _expiry -= 1 * assetCalendar
    # Retrieve options expiry date
    if expiryType == ExpType.OF:
        _expiry -= 3 * assetCalendar
    # Output __ho_nymex_exp__
    return _expiry

def __ng_nymex_exp__(assetCalendar, contractMonth, expiryType):
    """Get expiry dates for NG NYMEX contracts"""
    _expiry = None
    # Retrieve futures expiry date
    _expiry = date(contractMonth.year, contractMonth.month, 1)
    _expiry -= 3 * assetCalendar
    # Retrieve options expiry date
    if expiryType == ExpType.OF:
        _expiry -= 1 * assetCalendar
    # Output __ng_nymex_exp__
    return _expiry

def __wti_ice_exp__(assetCalendar, contractMonth, expiryType):
    """Get expiry dates for WTI ICE contracts"""
    _expiry = None
    # Retrieve options expiry date
    _expiry = __wti_nymex_exp__(assetCalendar, contractMonth, expiryType)
    # Retrieve first notice and futures expiry date
    if expiryType == ExpType.F or expiryType == ExpType.N:
        _expiry -= 1 * assetCalendar
    # Output __wti_ice_exp__
    return _expiry

def __br_ice_exp__(assetCalendar, contractMonth, expiryType):
    """Get expiry dates for BR ICE & NYMEX contracts"""
    _expiry = None
    _NEWEXPIRY = date(2016, 3, 1)
    # Retrieve old futures expiry date
    if contractMonth < _NEWEXPIRY:
        _expiry = date(contractMonth.year, contractMonth.month, 1)
        _expiry -= timedelta(days=15)
        if assetCalendar.onOffset(_expiry):
            _expiry -= 1 * assetCalendar
        else:
            _expiry -= 2 * assetCalendar
    # Retrieve new futures expiry date
    else:
        if contractMonth.month == 1:
            _expiry = date(contractMonth.year - 1, 12, 1)
        else:
            _expiry = date(contractMonth.year, contractMonth.month - 1, 1)
        _expiry -= 1 * assetCalendar
    # Christmas Day exception
    if contractMonth.month == 12:
        _XMASDAY = date(contractMonth.year, 12, 25) - 1 * assetCalendar
        _NYDAY = date(contractMonth.year - 1, 12, 1) - 1 * assetCalendar
        if _expiry == _XMASDAY or _expiry == _NYDAY:
            _expiry -= 1 * assetCalendar
    # Retrieve options expiry date
    if expiryType == ExpType.OF:
        _expiry -= 3 * assetCalendar
    # Output __br_ice_exp__
    return _expiry

def __go_ice_exp__(assetCalendar, contractMonth, expiryType):
    """Get expiry dates for GO ICE contracts"""
    _expiry = None
    # Retrieve futures expiry date
    _expiry = date(contractMonth.year, contractMonth.month, 14)
    _expiry -= 2 * assetCalendar
    # Retrieve options expiry date
    if expiryType == ExpType.OF:
        _expiry -= 5 * assetCalendar
    # Output __go_ice_exp__
    return _expiry

#-------------------------------------------------------------------------------
# Unit testing
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    _contract = date(2015, 12, 1)
    _asset = "WTI_NYMEX"
    _type ="f"
    _exp = get_expiry_date(_asset, _contract, _type)
    print(_exp)
    _type ="of"
    _exp = get_expiry_date(_asset, _contract, _type)
    print(_exp)
    _type ="n"
    _base = date.today()
    _exp = get_front_month(_asset, _base, _type)
    print(_exp)