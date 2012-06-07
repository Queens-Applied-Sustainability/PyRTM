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


class RTMConfig(dict):
    # TODO: implement white-list key checking
    # TODO: implement value validation
    pass


default_config = RTMConfig({
    # set up intelligible defaults
    'description': 'hello world',
    
    'day of year': 103,
    'time': 18.333, # GMT decimal hours
    'latitude': 44,
    'longitude': 283.7,
    
    'spectrum selector': 'lowtran 7',
    'filter function type': 0, # FIXME what does this mean (SBDART)
    'resolution': 0, # FIXME sbdart
    'lower limit': 0.25,
    'upper limit': 2.5,
    
    'zenith angle': 0,
    
    'atmosphere': 'mid-latitude summer',
    'aerosols': 'background stratospheric',
    'aerosol optical depth': 0.084, # FIXME units?
    
    'cloud altitude': [0, 0, 0, 0, 0], # FIXME ...
    'cloud optical depth': [0, 0, 0, 0, 0],
    
    'surface albedo type': 'vegetation',
    'surface elevation': 0.11, # km
})


class _RTM(object):
    """
    Abstract class describing interactions with RTM applications.
    """
    __metaclass__ = abc.ABCMeta
    
    executable = None
    input_file = None
    output_file = None
    
    def __init__(self, initconfig=None):
        self.config = RTMConfig(default_config)
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


class SBdart(_RTM):
    executable = 'drtx'
    input_file = 'INPUT'
    output_files = ['OUTPUT']


def All(*args, **kwargs):
    """
    Return an EachList containing all the RTM wrappers.
    
    Check out utils.EachList and the corresponding unit tests for more on how
    EachLists work.
    
    You can use this just like you'd use the RTM classes; everything will be
    the same except that all the results will be elements of an EachList.
    """
    return utils.EachList([SMARTS, SBdart])(*args, **kwargs)





