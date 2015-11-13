# -*- coding: utf-8 -*-

"""Settlement Module
Import Bloomberg data for settlement analysis
"""
__author__  = "Eric Pieuchot"
__date__    = "18 March 2015"

from datetime import datetime, timedelta
import comex.api.bbgapi as __API__
import pandas as __PD__
import numpy as __NP__
import logging
import math

__all__ = ['CloseAnalysis']

#------------------------------------------------------------------------------
# CloseAnalysis Object with vwap/twap functionality
#------------------------------------------------------------------------------

class CloseAnalysis(object):
    
        def __init__(self, bbgTicker = "CL1 Comdty", bbgTick = 0.01, settleWindow = 1,
                     settleTime = datetime.now().replace(microsecond=0)-timedelta(minutes=16)):
            try:
                _connection = __API__.Connection()
                if _connection.start_service():
                    _start = settleTime - timedelta(minutes=settleWindow)
                    _data = _connection.bdit(
                                            bbgTicker = bbgTicker,
                                            startTime = _start.isoformat(),
                                            endTime = settleTime.isoformat())
                    for _time in _data[("value")].keys():
                        _value = _data[("value")][_time]
                        _data[("value")][_time] = _value - math.fmod(_value, bbgTick)
                    if _connection.stop_service():
                        self.table = __PD__.DataFrame(_data).dropna(how="any")
            except:
                logging.critical("Error on API %s", _connection.__str__, exc_info=True)
            
        def get_vwap_and_twap(self, runningStat=False):
            _size = self.table.as_matrix(columns=["size"])
            _value = self.table.as_matrix(columns=["value"])
            _prod = _size * _value
            self.vwap = _prod.sum() / _size.sum()
            self.twap = _value.sum() / _value.size
            print("vwap: %s" %self.vwap)
            print("twap: %s" %self.twap)
            print("volume: %s" %_size.sum())
            print(self.table)
            self.table.value.plot(legend=True)
            self.table.size.plot(secondary_y=True)
            if runningStat:
                _cumsize = _size.cumsum(axis=0)
                _cumvalue = _value.cumsum(axis=0)
                _counter = __NP__.array([[i] for i in range(1,_value.size + 1)])
                _twap = _cumvalue / _counter
                _prod = _value * _size
                _cumprod = _prod.cumsum(axis=0)
                _vwap = _cumprod / _cumsize
                self.stat = __PD__.DataFrame(
                                        data=__NP__.column_stack((_vwap,_twap)),
                                        index=self.table.index,
                                        columns=["vwap","twap"])
                self.stat.plot()
            
if __name__ == "__main__":
    _analysis = CloseAnalysis()
    _analysis.get_vwap_and_twap(runningStat=True)
    del _analysis
                