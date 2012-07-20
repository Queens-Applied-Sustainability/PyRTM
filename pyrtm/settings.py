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
    
    'solar_constant': 1367,
    
    'year': 2012,
    'day_of_year': 103,
    'season': 'SUMMER',
    'time': 17, # GMT decimal hours
    'latitude': 44,
    'longitude': 283.7,
    'altitude': 0,
    'surface': 'vegetation',
    
    'atmosphere': 'sub-arctic summer',
    'average_daily_temperature': 15,
    'temperature': 15,
    'pressure': 1013.250,
    'relative_humidity': 35,
    'carbon_dioxide': 390,
    'pressure': 1013.250,
    
    'single_scattering_albedo': 0.8,
    'aerosol_optical_depth': 0.08,
    'angstroms_exponent': 1.1977,
    'aerosol_asymmetry': 0.6,
    
    'cloud': 0,
    
    'lower_limit': 0.28,
    'upper_limit': 2.5,
    'resolution': 0.01,
    'output': 'per wavelength',
    
    #'precipitable water': 0.5,
    #'ozone': 0.324,
    #'altitude'
    #'tropospheric nitrogen': '???',
    
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
            # Card 2 Mode 1
            'HEIGHT': 0,
            # Card 12 Mode 2
            'INTVL': 2,
            # Card 17 Mode 3
            'ZONE': 0,
        }
        for key, val in foreign.iteritems():
            native.update(getattr(self, key)(val))
        return native
    
    _surfaces = {#FIXME choices are fairly arbitrary
                 'snow': 3,
                 'clear water': 2,
                 'lake water': 35,
                 'sea water': 35,
                 'sand': 6,
                 'vegetation': 17,
                 'ocean water': 35}
    
    _atmospheres = {'tropical': 'TRL',
                    'mid-latitude summer': 'MLS',
                    'mid-latitude winter': 'MLW',
                    'sub-arctic summer': 'SAS',
                    'sub-arctic winter': 'SAW',
                    'us62': 'USSA'}
    
    description = lambda self, val: {'COMNT': "_".join(val[:64].split())}
    
    solar_constant = lambda self, val: {'SOLARC': val}
    
    longitude = lambda self, val: {'LONGIT': val}
    latitude = lambda self, val: {'LATIT': val}
    altitude = lambda self, val: {'ALTIT': val}
    year = lambda self, val: {'YEAR': val}
    day_of_year = lambda self, val: {
        'SUNCOR': utils.solar_distance_factor(val),
        'MONTH': utils.day_to_month_day(val)['MONTH'],
        'DAY': utils.day_to_month_day(val)['DAY'],
        }
    time = lambda self, val: {'HOUR': val}
    season = lambda self, val: {'SEASON': val}  # TODO.... auto-set?
    surface = lambda self, val: {'IALBDX': self._surfaces.get(val)}
    
    atmosphere = lambda self, val: {'ATMOS': self._atmospheres.get(val)}
    average_daily_temperature = lambda self, val: {'TAIR': val}
    temperature = lambda self, val: {'TDAY': val}
    pressure = lambda self, val: {'SPR': val}
    relative_humidity = lambda self, val: {'RH': val}
    carbon_dioxide = lambda self, val: {'qCO2': 390}
    
    single_scattering_albedo = lambda self, val: {'OMEGL': val}
    aerosol_optical_depth = lambda self, val: {'BETA': val}
    angstroms_exponent = lambda self, val: {'ALPHA1': val, 'ALPHA2': val}
    aerosol_asymmetry = lambda self, val: {'GG': val}
    
    cloud = lambda self, val: {}
    
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
    
    _outputs = {'none': 0, 'per wavelength': 1, 'integrated': 10}
    
    description = lambda self, val: {}
    
    solar_constant = lambda self, val: {} #TODO: do something with solfac?
    
    latitude = lambda self, val: {'ALAT': val}
    longitude = lambda self, val: {'ALON': val}
    altitude = lambda self, val: {'ZOUT': [val, 100]}
    day_of_year = lambda self, val: {'IDAY': val}
    season = lambda self, val: {}  # not supported
    time = lambda self, val: {'TIME': val}
    year = lambda self, val: {} # not supported
    
    surface = lambda self, val: {'ISALB': self._surfaces.get(val)}
    altitude = lambda self, val: {}#'ZPRES': val} only used for pressure
    
    atmosphere = lambda self, val: {'IDATM': self._atmospheres.get(val)}
    average_daily_temperature = lambda self, val: {} # not supported
    temperature = lambda self, val: {} # FIXME?
    pressure = lambda self, val: {'PBAR': val}
    relative_humidity = lambda self, val: {
        'UW': utils.rh_to_water(val, 15)} # FIXME self.temperature)}
    carbon_dioxide = lambda self, val: {'XCO2': val}
    
    single_scattering_albedo = lambda self, val: {}#defaulted'WBAER': val}
    aerosol_optical_depth = lambda self, val: {'TBAER': val, 'IAER': 2}
    angstroms_exponent = lambda self, val: {}#defaulted'ABAER': val}
    aerosol_asymmetry = lambda self, val: {}#defaulted'GBAER': val}
    
    cloud = lambda self, val: {'ZCLOUD': 6, 'TCLOUD': val}
    #cloud_altitude = lambda self, val: {'ZCLOUD': val} # FIXME?
    #cloud_optical_depth = lambda self, val: {'TCLOUD': val} # FIXME?
    
    #aersosols = lambda self, val: {'JAER': self._aerosols.get(val)}
    # TBAER is what we are itterating, with either rural or urban
    
    output = lambda self, val: {'IOUT': self._outputs.get(val)}
    lower_limit = lambda self, val: {'WLINF': val}
    upper_limit = lambda self, val: {'WLSUP': val}
    resolution = lambda self, val: {'WLINC': val}




