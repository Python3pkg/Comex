# -*- coding: utf-8 -*-

"""Module Asset
Asset static data, serialization methods and attached properties
"""

__author__ = "Eric Pieuchot"
__date__ = "29 May 2015"

# Possibility to switch between C-compiled and python xml parser
import comex.static as __DEF__
import comex.utility.config as __CFG__
import xml.etree.ElementTree as __ET__
import xml.dom.minidom as __DOM__

from pandas.tseries.offsets import CustomBusinessDay
from datetime import datetime

import logging as __LOG__
import csv
import os

__all__ = ['Assets', 'Asset', 'Commodity', 'Index']

#-------------------------------------------------------------------------------
# Asset Class and its Commodity/Index implementation
#-------------------------------------------------------------------------------

class Asset(object):
    '''Parent asset class'''

    def __init__(self, name="", currency="", ticker="", calendar=""):
        self.name, self.currency = name, currency
        self.ticker, self.calendar = ticker, calendar
    
    def get_custom_date(self):
        """Return Pandas CustomBusinessDay based on .txt"""
        _hol_center = None
        _config = __CFG__.Config()
        if _config.add_section(__DEF__.CONFIG_SECTION_CALENDAR):
            _cal = self.calendar.lower()
            if _config.has_key(_cal):
                try:
                    _file = os.path.join(__DEF__.PROJECT_ROOT, _config[_cal])
                    with open(_file, 'r') as _txt:
                        _week_mask = "Mon Tue Wed Thu Fri"
                        _hol_mask = [_lgn.pop() for _lgn in csv.reader(_txt)]
                        _hol_center = CustomBusinessDay(holidays=_hol_mask,
                                                        weekmask=_week_mask)
                except IOError:
                    logging.critical("Failing %s", _config[_cal], exc_info=True)
            else:
                logging.warning("Missing %s", _cal, exc_info=True)
        else:
            logging.error("Reading %s", __DEF__.CONFIG_SECTION_CALENDAR, exc_info=True)
        # Output get_custom_date
        return _hol_center

class Commodity(Asset):
    "Child commodity class implementing asset"
    def __init__(self, name="", currency="", ticker="", calendar="",
                 lot=1, factor=1, close="19:30:00", vwap=1, cycle=[],
                 family=__DEF__.ComType.Unknown):
        self.lot, self.factor = lot, factor
        self.close, self.vwap = datetime.strptime(close, "%H:%M:%S"), vwap
        self.cycle, self.family = cycle, family
        super(Commodity, self).__init__(name, currency, ticker, calendar)

class Index(Asset):
    "Child index class implementing asset"
    def __init__(self, name="", currency="", ticker="", calendar="",
                 divisor=1, basket={}):
        self.divisor, self.basket = divisor, basket
        super(Index, self).__init__(name, currency, ticker, calendar)

#-------------------------------------------------------------------------------
# Assets dictionary with serialization methods
#-------------------------------------------------------------------------------

class Assets(dict):
    """Dictionary of assets - commodity and indices"""
    
    def __init__(self):
        # Boolean to check if XML loaded
        _config = __CFG__.Config()
        if _config.add_section(__DEF__.CONFIG_SECTION_SETTING):
            _name = _config["asset_file"]
            self._file = os.path.join(__DEF__.PROJECT_ROOT, _name)
        else:
            logging.error("Error on adding %s", __DEF__.CONFIG_SECTION_SETTING,
                          exc_info=True)
    
    def py_to_xml(self):
        """Serialize pyasset into XML"""
        _serialized = False
        # Test if pyasset dictionary has any element
        if len(self) != 0:
            # Create XML document root
            _root = __ET__.Element("assets")
            _root.set("exported", datetime.today().strftime("%d-%m-%Y %H:%M:%S"))
            # Browse through pyasset items
            for _asset in self.values():
                # Check element as class instance
                if isinstance(_asset, Asset):
                    _element = __ET__.SubElement(_root, "asset")
                    __ET__.SubElement(_element,"name").text = str(_asset.name)
                    __ET__.SubElement(_element,"currency").text = str(_asset.currency)
                    __ET__.SubElement(_element,"ticker").text = str(_asset.ticker)
                    __ET__.SubElement(_element,"calendar").text = str(_asset.calendar)
                    # Check commodity implementation
                    if isinstance(_asset, Commodity):
                        _element.set("type", "commodity")
                        __ET__.SubElement(_element,"lot").text = str(_asset.lot)
                        __ET__.SubElement(_element,"factor").text = str(_asset.factor)
                        __ET__.SubElement(_element,"close").text = str(_asset.close.strftime("%H:%M:%S"))
                        __ET__.SubElement(_element,"vwap").text = str(_asset.vwap)
                        __ET__.SubElement(_element,"family").text = str(_asset.family.name)
                        _parent = __ET__.SubElement(_element,"cycle")
                        for _item in _asset.cycle:
                            __ET__.SubElement(_parent,"code").text = str(_item.name)
                    # Check index implementation
                    elif isinstance(_asset, Index):
                        _element.set("type", "index")
                        __ET__.SubElement(_element,"divisor").text = str(_asset.divisor)
                        _parent = __ET__.SubElement(_element,"basket")
                        for _item in _asset.basket.items():
                            _child = __ET__.SubElement(_parent,"constituent")
                            _child.set("contract", str(_item[0]))
                            _child.set("weight", str(_item[1]))
            # Write XML file onto drive
            try:
                # DOM API for pretty formatting
                _reparsed = __DOM__.parseString(__ET__.tostring(_root))
                _reparsed.writexml(open(self._file, 'w'),
                                   indent="  ",
                                   addindent="  ",
                                   newl='\n')
                _serialized = True
            except:
                logging.critical("Error on saving %s", self._file,
                                         exc_info=True)
                _serialized = False
        return _serialized                    
    
    def xml_to_py(self):
        """Deserialize XML into pyasset"""
        _deserialized = False
        try:
            # Create etree root
            _root = __ET__.parse(self._file).getroot()
            # Browse through elements in root
            for _element in _root:
                _type = _element.get("type")
                # Create commodity child class instance
                if _type == "commodity":
                    _asset = Commodity()
                    _asset.lot = float(_element.findtext("lot"))
                    _asset.factor = float(_element.findtext("factor"))
                    _asset.close = datetime.strptime(_element.findtext("close"),"%H:%M:%S")
                    _asset.vwap = float(_element.findtext("vwap"))
                    _asset.family = __DEF__.ComType[_element.findtext("family")]                   
                    _asset.cycle = [
                                    __DEF__.FutCode[_child.text]
                                    for _child in _element.find("cycle").iter("code")]
                # Create index child class instance
                elif _type == "index":
                    _asset = Index()
                    _asset.divisor = float(_element.findtext("divisor"))
                    _asset.basket ={
                                    str(_child.get("contract")):float(_child.get("weight"))
                                    for _child in _element.find("basket").iter("constituent")}
                # Add back asset parent class properties
                _asset.name = _element.findtext("name")
                _asset.currency = _element.findtext("currency")
                _asset.ticker = _element.findtext("ticker")
                _asset.calendar = _element.findtext("calendar")
                # Populate pyasset dictionary
                self[_asset.name] = _asset
                _deserialized = True
        except:
            # Trap corrupted file or pathname
            logging.critical("Error on file %s", self._file, exc_info=True)
            _deserialized = False
        return _deserialized

#-------------------------------------------------------------------------------
# Unit testing
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    # create commodity class instance
    _commodity = Commodity("WTI_NYMEX", "USD", "CL", "NYM",
                           1000, 1, "19:30:00", 1)
    _commodity.cycle = [__DEF__.FutCode.F, __DEF__.FutCode.G,
                        __DEF__.FutCode.H, __DEF__.FutCode.J,
                        __DEF__.FutCode.K, __DEF__.FutCode.M,
                        __DEF__.FutCode.N, __DEF__.FutCode.Q,
                        __DEF__.FutCode.U, __DEF__.FutCode.V,
                        __DEF__.FutCode.X, __DEF__.FutCode.Z]
    _commodity.family = __DEF__.ComType.NRG
    # Create index class instance
    _index = Index("SPGSCLP", "USD", "SPGSCLP", "NYC", 1)
    _index.basket = {"CLN5":0.5, "CLQ5":0.5}
    # Create assets class instance
    _assets = Assets()
    _assets[_commodity.name] = _commodity
    _assets[_index.name] = _index
    # Test pyclass serialization / deserialization
    print(_assets.keys())
    print(_assets.py_to_xml())
    del _commodity, _index, _assets
    _assets = Assets()
    print(_assets.xml_to_py())
    print(_assets.keys())