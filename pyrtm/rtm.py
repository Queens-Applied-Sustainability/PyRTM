"""
    Copyright (c) 2012 Philip Schliehauf (uniphil@gmail.com) and the
    Queen's University Applied Sustainability Centre
    
    This project is hosted on github; for up-to-date code and contacts:
    https://github.com/Queens-Applied-Sustainability/PyRTM
    
    This file is part of PyRTM.

    PyRTM is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyRTM is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyRTM.  If not, see <http://www.gnu.org/licenses/>.
"""

import abc
import utils
import settings


class _RTM(object):
    """
    Abstract class describing interactions with RTM applications.
    """
    __metaclass__ = abc.ABCMeta
    
    executable = None
    input_file = None
    output_file = None
    
    def __init__(self, initconfig=None):
        self.config = utils.RTMConfig(settings.default_config)
        if initconfig:
            self.config.update(initconfig)
    
    def __call__(self, newconfig={}):
        self.config.update(newconfig)
        self.write_input_file()
        self.run_rtm()
        # get the results out
        return "results!"
    
    @abc.abstractmethod
    def write_input_file(self):
        return
    
    @abc.abstractmethod
    def run_rtm(self):
        returns


class SMARTS(_RTM):
    executable = 'smarts295'
    input_file = 'smarts295.inp.txt'
    output_files = ['smarts295.out.txt']
    
    def write_input_file(self):
        return # FIXME
    def run_rtm(self):
        return # FIXME


class SBdart(_RTM):
    executable = 'drtx'
    input_file = 'INPUT'
    output_files = ['OUTPUT']
    
    _translate = settings.translate('SBdart') # returns a dict
    
    def write_input_file(self):
        rtm_vars = {
            'ALAT': self.config['latitude'],
            'ALON': self.config['longitude'],
            'IDAY': self.config['day of year'],
            'TIME': self.config['time'],
            #'IOUT': self._translate['output'][self.config['output type']],
            'wlinf': self.config['lower limit'],
            'wlsup': self.config['upper limit'],
            'wlinc': self.config['resolution'],
            'ISALB': self._translate['surface'][self.config['surface albedo']],
            'ZPRES': self.config['surface elevation'],
            'IDATM': self._translate['atmosphere'][self.config['atmosphere']],
            'Zcloud': self.config['cloud altitude'],
            'Tcloud': self.config['cloud optical depth'],
            'JAER': self._translate['aerosols'][self.config['aerosols']],
        }
        
    def run_rtm(self):
        return # FIXME


def All(*args, **kwargs):
    """
    Return an EachList containing all the RTM wrappers.
    
    Check out utils.EachList and the corresponding unit tests for more on how
    EachLists work.
    
    You can use this just like you'd use the RTM classes; everything will be
    the same except that all the results will be elements of an EachList.
    """
    return utils.EachList([SMARTS, SBdart])(*args, **kwargs)





