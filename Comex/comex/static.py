# -*- coding: utf-8 -*-

"""Definition module
Generic global variables/constants
"""

__author__ = "Eric Pieuchot"
__date__ = "8 Jul 2015"

from os.path import dirname, join
from logging import ERROR, DEBUG
from enum import Enum

__all__ = ['ComType',
           'FutCode',
           'ROOT_DATA',
           'ROOT_PROJECT',
           'LOGGING_FILE',
           'LOGGING_FORMAT',
           'LOGGING_LEVEL_FILE',
           'LOGGING_LEVEL_CONSOLE',
           'CONFIG_FILE',
           'CONFIG_SECTION_SETTING',
           'CONFIG_SECTION_CALENDAR']

#-------------------------------------------------------------------------------
# Path
#-------------------------------------------------------------------------------

ROOT_PROJECT = dirname(__file__)
ROOT_DATA = join(ROOT_PROJECT,"data")

#-------------------------------------------------------------------------------
# Logging
#-------------------------------------------------------------------------------

LOGGING_FILE = "error.log"
LOGGING_FORMAT = "%(asctime)s [%(module)s] [%(levelname)s] %(message)s"
LOGGING_LEVEL_FILE = ERROR
LOGGING_LEVEL_CONSOLE = DEBUG

#-------------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------------

CONFIG_FILE = "config.ini"
CONFIG_SECTION_SETTING = "Setting"
CONFIG_SECTION_CALENDAR = "Calendar"

#-------------------------------------------------------------------------------
# Enum
#-------------------------------------------------------------------------------

class ComType(Enum):
    """Enum type for commodity futures family"""
    Unknown, AGS, NRG, MTL, PGM = 0, 1, 2, 3, 4

class FutCode(Enum):
    """Enum type for commodity futures contract month"""
    Unknown, F, G, H, J, K, M = 0, 1, 2, 3, 4, 5, 6
    N, Q, U, V, X, Z = 7, 8, 9, 10, 11, 12