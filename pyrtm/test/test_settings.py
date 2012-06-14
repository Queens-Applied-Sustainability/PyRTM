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


import utils


default_config = utils.RTMConfig({
    'description': 'Hello World -- Default Config',

    'day of year': 103,
    'time': 19.0, # GMT decimal hours
    'latitude': 44,
    'longitude': 283.7,
    
    'lower limit': 0.25,
    'upper limit': 2.5,
    
    #'precipitable water': 0.5,
    #'ozone': 0.324,
    #'tropospheric nitrogen': '???',
    #'surface pressure': '???',
    
})


"""

precip water (temp(database) and rel humidity(database))
ozone (database)
nitrogen tropospheric [database]
surface pressure [where available]
later -- stratsopheric (smog) [???; not much effect on spectrum -- maybe based on proximity to city]
later -- cloud cover from cloud photos?

iterating on TAERST or DBAER

SMARTS for clear days
SBdart for cloudy days

"""



""" Old testing defaults

    # set up intelligible defaults
    'description': 'hello world',
    
    'day of year': 103,
    'time': 18.333, # GMT decimal hours
    'latitude': 44,
    'longitude': 283.7,
    
    'spectrum selector': 'lowtran 7',
    'filter function': 0, # FIXME what does this mean (SBDART)
    'resolution': 0, # FIXME sbdart
    'lower limit': 0.25,
    'upper limit': 2.5,
    
    'zenith angle': 0,
    
    'atmosphere': 'mid-latitude summer',
    'aerosols': 'background stratospheric',
    'aerosol optical depth': 0.084, # FIXME units?
    
    'cloud altitude': [0, 0, 0, 0, 0], # FIXME ...
    'cloud optical depth': [0, 0, 0, 0, 0],
    
    'surface albedo': 'vegetation',
    'surface elevation': 0.11, # km
"""

_translation = {}
    
_translation['SBdart'] = {
    'params': {
        'latitude': 'ALAT',
        'longitude': 'ALON',
        'day of year': 'IDAY',
        'time': 'TIME',
        'output': 'IOUT',
        'lower limit': 'wlinf',
        'upper limit': 'wlsup',
        'resolution': 'wlinc',
        'surface albedo': 'ISALB',
        'surface elevation': 'ZPRES',
        'atmosphere': 'IDATM',
        'cloud altitude': 'Zcloud',
        'cloud optical depth': 'Tcloud',
        'aerosols': 'JAER',
    },
    'output': {
        'none': 0,
        'per wavelength': 1,
    },
    'surface': {
        'snow': 1,
        'clear water': 2,
        'lake water': 3,
        'sea water': 4,
        'sand': 5,
        'vegetation': 6,
        'ocean water': 7
    },
    'atmosphere': {
        'tropical': 1,
        'mid-latitude summer': 2,
        'mid-latitude winter': 3,
        'sub-arctic summer': 4,
        'sub-arctic winter': 5,
        'us62': 6
    },
    'aerosols': {
        'no aerosol': 0,
        'background stratospheric': 1,
        'aged volcanic': 2,
        'fresh volcanic': 3,
        'meteor dust': 4
    },
}

_translation['SMARTS'] = {
    'atmosphere': {
        'tropical': 'TRL',
        'mid-latitude summer': 'MLS',
        'mid-latitude winter': 'MLW',
        'sub-arctic summer': 'SAS',
        'sub-arctic winter': 'SAW',
        'us62': 'USSA',
    },
    'aerosols': {
        'rural': 'S&F_RURAL',
        'urban': 'S&F_URBAN',
        'maritime': 'S&F_MARIT',
        'tripospheric': 'S&F_TROPO',
        
        'continental': 'SRA_CONTL',
        'urban': 'SRA_URBAN',
        'maritime': 'SRA_MARIT',
        
        'Braslau & Dave C': 'B&D_C',
        'Braslau & Dave C1': 'B&D_c1',
        
        'desert': 'DESERT_MIN',
        'crazy desert': 'DESERT_MAX',
        
        'custom': 'USER',
        
        # FIXME ...
        'background stratospheric': 'B&D_C',
    },
}

def translate(rtm):
    return _translation.get(rtm)





