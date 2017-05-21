# -*- coding: utf-8 -*-

"""Config Module
Generic configuration file
"""

__author__ = "Eric Pieuchot"
__date__ = "8 Jul 2015"

from logging import critical, error, warning
from configparser import ConfigParser
import comex.static as __DEF__

__all__ = ['Config']

#-------------------------------------------------------------------------------
# Config Class and its underlying Sections
#-------------------------------------------------------------------------------

class Config(dict):
    '''Import config.ini file from project root directory'''

    def __init__(self, fileName=__DEF__.CONFIG_FILE):
        # Initialize parser object
        self._parser = ConfigParser()
        try:
            # Read .ini file
            self._file = __DEF__.join(__DEF__.ROOT_DATA, fileName)
            self._parser.read(self._file)
        except:
            critical("Exception on file %s", self._file, exc_info=True)
    
    def add_section(self, section=__DEF__.CONFIG_SECTION_SETTING):
        """
        Create dictionary object from [Section] in config.ini file
        
        Notes
        -----
        Concatenate with existing elements, replace duplicates
        """
        # Initialize dict
        _dict = {}
        try:
            # Load [Section] from parser object
            _options = self._parser.options(section)
            for _option in _options:
                # Remove duplicate
                if _option in self: del self[_option]
                try:
                    # Add 'settings:' from [section]
                    _dict[_option] = self._parser.get(section, _option)
                except:
                    warning("Exception on %s", _option, exc_info=True)
                    _dict[_option] = None
                    return False
            # Concatenate dictionaries
            self.update(_dict)
            return True
        except:
            error("No section %s", section, exc_info=True)
            return False

#-------------------------------------------------------------------------------
# Unit testing
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    # Unit testing
    _test = Config()
    _test.add_section()
    _test.add_section(__DEF__.CONFIG_SECTION_CALENDAR)
    print((list(_test.keys())))