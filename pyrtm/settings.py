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


default_config = {
    'description': 'Hello World -- Default Config',

    'day_of_year': 103,
    'time': 14.0, # GMT decimal hours
    'latitude': 44,
    'longitude': 283.7,
    
    'lower_limit': 0.28,
    'upper_limit': 2.5,
    
    'output': 'per wavelength',
    
    #'precipitable water': 0.5,
    #'ozone': 0.324,
    #'altitude'
    #'tropospheric nitrogen': '???',
    #'surface pressure': '???',
    
}

"""
later -- stratsopheric (smog) [???; not much effect on spectrum -- maybe based on proximity to city]
later -- cloud cover from cloud photos?

iterating on TAERST or DBAER
"""

@utils.instantiator
class translate_smarts(utils._Translation):
    "Translates both keys and values where appropriate for use with SMARTS"
    
    def __call__(self, foreign):
        native = {
            # Card 1
            'COMNT': 'Hello_World',
            # Card 2 Mode 1
            'SPR': 1000,
            'ALTIT': 0,
            'HEIGHT': 0,
            # Card 3 Mode 0
            'TAIR': 15, # temp at site-level
            'RH': 50,
            'SEASON': 'SUMMER',
            'TDAY': 7, # average daily temp
            # Card 7
            'qCO2': 390, # ppm CO2
            # Card 8 Mode USER
            'ALPHA1': 1,
            'ALPHA2': 1,
            'OMEGL': 0.8,
            'GG': 0.8,
            # Card 9 Mode 1
            'BETA': 1,
            # Card 11
            'WLMN': 280,
            'WLMX': 4000,
            'SUNCOR': 1,
            'SOLARC': 1367,
            # Card 12 Mode 2
            'WPMN': 280,
            'WPMX': 4000,
            'INTVL': 2,
            # Card 17 Mode 3
            'YEAR': 2012,
            'MONTH': 6,
            'DAY': 14,
            'HOUR': 12,
            'LATIT': 44,
            'LONGIT': -73,
            'ZONE': -5,
        }
        for key, val in foreign.iteritems():
            native.update(getattr(self, key)(val))
        return native
    
    _atmospheres = {'tropical': 'TRL',
                    'mid-latitude summer': 'MLS',
                    'mid-latitude winter': 'MLW',
                    'sub-arctic summer': 'SAS',
                    'sub-arctic winter': 'SAW',
                    'us62': 'USSA'}
                    
    _aerosols = {'rural': 'S&F_RURAL',
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
                 'background stratospheric': 'B&D_C'}
    
    description = lambda self, val: {'COMNT': "_".join(val[:64].split())}
    longitude = lambda self, val: {'LONGIT': val}
    latitude = lambda self, val: {'LATIT': val}
    def day_of_year(self, val):
        month = 0 # FIXME
        day = 5 # FIXME
        return {'MONTH': month, 'DAY': day}
    time = lambda self, val: {'HOUR': val}
    atmosphere = lambda self, val: {'ATMOS': self._atmospheres.get(val)}
    aerosols = lambda self, val: {'AEROS': self._aerosols.get(val)}
    lower_limit = lambda self, val: {'WLMN': val*1000, 'WPMN': val*1000}
    upper_limit = lambda self, val: {'WLMX': val*1000, 'WPMX': val*1000}
    resolution = lambda self, val: {'WLINC': val}
    output = lambda self, val: {}


@utils.instantiator
class translate_sbdart(utils._Translation):
    "Translates both keys and values where appropriate for use with SBdart"
    
    _surfaces = {'snow': 1,
                 'clear water': 2,
                 'lake water': 3,
                 'sea water': 4,
                 'sand': 5,
                 'vegetation': 6,
                 'ocean water': 7}
    
    _atmospheres = {'tropical': 1,
                    'mid-latitude summer': 2,
                    'mid-latitude winter': 3,
                    'sub-arctic summer': 4,
                    'sub-arctic winter': 5,
                    'us62': 6}
    
    _aerosols = {'no aerosol': 0,
                 'background stratospheric': 1,
                 'aged volcanic': 2,
                 'fresh volcanic': 3,
                 'meteor dust': 4}
    
    _outputs = {'none': 0, 'per wavelength': 1}
    
    description = lambda self, val: {}
    
    latitude = lambda self, val: {'ALAT': val}
    longitude = lambda self, val: {'ALON': val}
    day_of_year = lambda self, val: {'IDAY': val}
    time = lambda self, val: {'TIME': val}
    
    surface_albedo = lambda self, val: {'ISALB': self._surfaces.get(val)}
    surface_elevation = lambda self, val: {'ZPRES': val}
    
    atmosphere = lambda self, val: {'IDATM': self._atmospheres.get(val)}
    cloud_altitude = lambda self, val: {'ZCLOUD': val} # FIXME?
    cloud_optical_depth = lambda self, val: {'TCLOUD': val} # FIXME?
    
    #aersosols = lambda self, val: {'JAER': self._aerosols.get(val)}
    # TBAER is what we are itterating, with either rural or urban
    
    output = lambda self, val: {'IOUT': self._outputs.get(val)}
    lower_limit = lambda self, val: {'WLINF': val}
    upper_limit = lambda self, val: {'WLSUP': val}
    resolution = lambda self, val: {'WLINC': val}




