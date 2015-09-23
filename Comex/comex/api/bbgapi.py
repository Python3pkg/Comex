# -*- coding: utf-8 -*-

"""Bloomberg Module
Manipulate Bloomberg Python API
"""
__author__  = "Eric Pieuchot"
__date__    = "18 March 2015"

from datetime import datetime, timedelta, date
from collections import defaultdict
import logging
import blpapi

__all__ = ['Connection']

#------------------------------------------------------------------------------
# Bbg //blp/refdata service connection
#------------------------------------------------------------------------------
 
class Connection(object):
    
    def __init__(self, host = "localhost", port = 8194):
        """
        Starting bloomberg API session
        """
        # Fill SessionOptions
        _options = blpapi.SessionOptions()
        _options.setServerHost(host)
        _options.setServerPort(port)
        # Create a Session
        self._session = blpapi.Session(_options)
        
    def start_service(self, service = "//blp/refdata"):
        """
        Initialize Bloomberg refData service
        """
        # Start a session
        if self._session.start():
            self._session.nextEvent()
            # Open a service
            if self._session.openService(service):
                self._session.nextEvent()
                # Obtain previously opened service
                self._service = self._session.getService(service)
                self._session.nextEvent()
                return True
            else:
                logging.error("Error on service %s", self._service.name,
                              exc_info=True)
                return False
        else:
            logging.critical("Error on blpapi session", exc_info=True)
            return False
    
    def stop_service(self):
        """
        Stop Bloomberg refData service
        """
        if self._session.stop():
            del self._service
            return True
        else:
            logging.error("Error on service %s", self._service.name,
                          exc_info=True)
            return False

#------------------------------------------------------------------------------
# Bbg HistoricalDataRequest
#------------------------------------------------------------------------------
 
    def bdh(
            self, bbgTickers = ["CL1 Comdty"], bbgFields = ["Px_Last"],
            startDate = "%s -1CY" % date.today().strftime("%Y%m%d"), 
            endDate = date.today().strftime("%Y%m%d"), 
            periodSelection = "DAILY", periodFill = "ACTIVE_DAYS_ONLY"):
        """
        Description
        -----------
        Bloomberg Historical Data Request (several tickers available per call)
        
        Parameters
        ----------
            bbgTickers/bbgFields (string array): bloomberg tickers and fields
        
            startDate/endDate (date): ISOformat yyyymmdd
        
            periodSelection (string): options DAILY, WEEKLY, MONTHLY...
        
            periodFill (string): options ALL_CALENDAR_DAYS, ACTIVE_DAYS_ONLY...
        
        Examples
        --------
            functionReturn (defaultdict): from Bloomberg response object::
            
                >>> comex.pytool.pybbg.bdh()
                { (string, string) { datetime.date : float, ...} : ...}
        """
        # Create an "HistoricalDataRequest" request
        _request = self._service.createRequest("HistoricalDataRequest")    
        _request.set("nonTradingDayFillOption", periodFill)
        _request.set("periodicitySelection", periodSelection)
        _request.set("startDate", startDate)
        _request.set("endDate", endDate)
        for _ticker in bbgTickers:
            _request.append("securities",_ticker)
        for _field in bbgFields:
            _request.append("fields",_field)
        # Send the request
        self._session.sendRequest(_request)
        logging.info("Sending request %s", _request.toString(), exc_info=True)
        _response = defaultdict(dict)
        # Process received events
        while(True):
            try:
                _event = self._session.nextEvent(500)
                for _msg in _event:
                    #HistoricalDataResponse only for a single security
                    _securitydata = _msg.getElement("securityData")
                    _ticker = _securitydata.getElementAsString("security")
                    _fielddataarray = _securitydata.getElement("fieldData")
                    for i in range(_fielddataarray.numValues()):
                        _fielddata = _fielddataarray.getValueAsElement(i)
                        for j in range(1,_fielddata.numElements()):
                            _date = _fielddata.getElement(0).getValueAsDatetime()
                            _value = _fielddata.getElement(j).getValueAsFloat()
                            _response[(_ticker, bbgFields[j-1])][_date] = _value
                if _event.eventType() == blpapi.Event.RESPONSE:
                    # Response completly received, so we could exit
                    logging.info("Request fully received", exc_info=True)
                    break
            except:
                logging.error("Error on response %s", _event.REQUEST_STATUS,
                              exc_info=True)
        return _response

#------------------------------------------------------------------------------
# Bbg IntradayTickRequest
#------------------------------------------------------------------------------
 
    def bdit(
            self, bbgTicker = "CL1 Comdty", eventTypes = ["TRADE", "AT_TRADE"],
            startTime = (datetime.now().replace(microsecond=0)-timedelta(minutes=16)).isoformat(),
            endTime = (datetime.now().replace(microsecond=0)-timedelta(minutes=15)).isoformat()):
        """
        Description
        -----------
        Bloomberg Intraday Tick Request (only one ticker available per call)
        
        Parameters
        ----------
            bbgTicker (string): bloomberg ticker
        
            startTime/endTime (datetime): ISOformat yyyy-mm-ddThh:mm:ss
        
            eventTypes (string array): options TRADE, AT_TRADE, BID, ASK...
        
        Examples
        --------
            functionReturn (defaultdict): from Bloomberg response object::
            
                >>> comex.pytool.pybbg.bdit()
                { (string) { datetime.datetime : float, ...} : ...}
        """
        # Create an "IntradayTickRequest" request
        _request = self._service.createRequest("IntradayTickRequest")          
        _request.set("security", bbgTicker)
        _request.set("startDateTime", startTime)
        _request.set("endDateTime", endTime)
        for _eventtype in eventTypes:
            _request.append("eventTypes",_eventtype)        
        # Send the request       
        self._session.sendRequest(_request)
        logging.info("Sending request %s", _request.toString(), exc_info=True)
        _response = defaultdict(dict)
        _fields = ["value", "size"]
        # Process received events
        while(True):
            try:
                _event = self._session.nextEvent(500)
                for _msg in _event:
                    _securitydata = _msg.getElement("tickData")
                    _tickdataarray = _securitydata.getElement("tickData")
                    for i in range(_tickdataarray.numValues()):
                        _tickdata = _tickdataarray.getValueAsElement(i)
                        _time = _tickdata.getElementAsDatetime("time")
                        _size = _tickdata.getElementAsFloat("size")
                        # Aggregate data per time stamp keys (in seconds)
                        if _size > 0:                        
                            for j in range(len(_fields)):
                                _value = _tickdata.getElementAsFloat(_fields[j])
                                if _response[(_fields[j])].has_key(_time):
                                    if _fields[j] == "value":
                                        _response[(_fields[j])][_time] += _size*_value
                                    else:
                                        _response[(_fields[j])][_time] += _value
                                else:
                                    if _fields[j] == "value":
                                        _response[(_fields[j])][_time] = _size*_value
                                    else:
                                        _response[(_fields[j])][_time] = _value
                if _event.eventType() == blpapi.Event.RESPONSE:
                    # Response completly received, so we could exit
                    logging.info("Request fully received", exc_info=True)
                    # Retrieve average "value" per time stamp
                    for _time in _response[("value")].keys():
                        _size = _response[("size")][_time]
                        if _size > 1: _response[("value")][_time] /= _size
                    break
            except:
                logging.error("Error on response %s", _event.REQUEST_STATUS,
                              exc_info=True)
        return _response

#------------------------------------------------------------------------------
# Bbg IntradayBarRequest
#------------------------------------------------------------------------------
 
    def bdib(
            self, bbgTicker = "CL1 Comdty", eventType = "TRADE",eventInterval = 1,
            startTime = (datetime.now().replace(microsecond=0)-timedelta(minutes=16)).isoformat(),
            endTime = (datetime.now().replace(microsecond=0)-timedelta(minutes=15)).isoformat()):
        """
        Description
        -----------
        Bloomberg Intraday Bar Request (only one ticker available per call)
        
        Parameters
        ----------
            bbgTicker (string): bloomberg ticker
        
            startTime/endTime (datetime): ISOformat yyyy-mm-ddThh:mm:ss
        
            eventType (string): options TRADE, AT_TRADE, BID, ASK...
        
        Examples
        --------
            functionReturn (defaultdict): from Bloomberg response object::
            
                >>> comex.pytool.pybbg.bdib()
                { (string) { datetime.datetime : float, ...} : ...}
        """
        # Create an "IntradayBarRequest" request
        _request = self._service.createRequest("IntradayBarRequest")
        _request.set("security", bbgTicker)
        _request.set("eventType", eventType)
        _request.set("interval", eventInterval)
        _request.set("startDateTime", startTime)
        _request.set("endDateTime", endTime)
        # Send the request       
        self._session.sendRequest(_request)
        logging.info("Sending request %s", _request.toString(), exc_info=True)
        _response = defaultdict(dict)
        _fields = ["low", "high", "volume"]
        # Process received events
        while(True):
            try:
                _event = self._session.nextEvent(500)
                for _msg in _event:
                    _bardata = _msg.getElement("barData")
                    _bartickdataarray = _bardata.getElement("barTickData")
                    for i in range(_bartickdataarray.numValues()):
                        _bartickdata = _bartickdataarray.getValueAsElement(i)
                        for j in range(len(_fields)):
                            _time = _bartickdata.getElementAsDatetime("time")
                            _value = _bartickdata.getElement(_fields[j]).getValue()
                            _response[(_fields[j])][_time] = _value
                if _event.eventType() == blpapi.Event.RESPONSE:
                    # Response completly received, so we could exit
                    logging.info("Request fully received", exc_info=True)
                    break
            except:
                logging.error("Error in processing response %s",
                              _event.REQUEST_STATUS, exc_info=True)
        return _response

#------------------------------------------------------------------------------
# Unit Testing
#------------------------------------------------------------------------------

if __name__ == "__main__":
    #Testing unit for Bloomberg Python 2.7 API
    import pandas as PD
    _connection = Connection()
    print(_connection.start_service())
    _data = _connection.bdh()
    _table = PD.DataFrame(_data)
    _table.plot()
    del _data
    del _table
    _data = _connection.bdit()
    _table = PD.DataFrame(_data)
    print(_table)
    del _data
    del _table
    _connection.stop_service()
    