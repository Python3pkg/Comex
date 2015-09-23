# -*- coding: utf-8 -*-

"""Module Logging
Generic file and console logger configuration
"""

__author__ = "Eric Pieuchot"
__date__ = "28 May 2015"

import comex.static as __DEF__
import logging as __LOG__

__all__ = ['start_logging']

#-------------------------------------------------------------------------------
# Unit testing
#-------------------------------------------------------------------------------

def start_logging(fileName=__DEF__.LOGGING_FILE):
    """Initialize logging object and setup console/file handler"""
    # Get root logger
    _logger = __LOG__.getLogger()
    # Create formatter
    _formatter = __LOG__.Formatter(fmt=__DEF__.LOGGING_FORMAT,
                                   datefmt="%Y-%m-%d %H:%M:%S")
    # Create console handler and set name/level/format
    _consolehandler = __LOG__.StreamHandler()
    _consolehandler.set_name("console_handler")
    _consolehandler.setLevel(__DEF__.LOGGING_LEVEL_CONSOLE)
    _consolehandler.setFormatter(_formatter)
    # Create file handler and set name/level/format
    _file = __DEF__.join(__DEF__.ROOT_DATA, fileName)
    _filehandler = __LOG__.FileHandler(_file, mode='w')
    _filehandler.set_name("file_handler")
    _filehandler.setLevel(__DEF__.LOGGING_LEVEL_FILE)
    _filehandler.setFormatter(_formatter)
    # Add console and file handlers to logger
    _logger.addHandler(_consolehandler)
    _logger.addHandler(_filehandler)
    # Return Output
    return True

#-------------------------------------------------------------------------------
# Unit testing
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    # Unit testing
    print(start_logging())
    __LOG__.debug("Debug message")
    __LOG__.info("Info message")
    __LOG__.warning("Warning message")
    __LOG__.error("Error message")
    __LOG__.critical("Critical message")