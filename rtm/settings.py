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

from dateutil.parser import parse as parsedt

defaults = {
    'description': 'Default Config', # use internally; any string
    
    'solar_constant': 1367, # W/m^2 in space
    
    'season': 'summer', # summer or winter
    'time': parsedt('2012-10-11 12:00:00 -0500'), # specifying tz is important!
    'latitude': 44, # degrees, north-positive
    'longitude': 283.7, # degrees, east-positive
    'elevation': 0, # metres above sea level
    'surface_type': 'vegetation', # see docs for valid options
    'single_scattering_albedo': 0.8,

    'atmosphere': 'sub-arctic summer', # see docs for valid options
    'average_daily_temperature': 15, # degrees C
    'temperature': 15, # degrees C
    'pressure': 1013.250, # mb
    'relative_humidity': 35, # %
    'angstroms_coefficient': 0.08,
    'angstroms_exponent': 1.1977,
    'aerosol_asymmetry': 0.6, 
    'boundary_layer_ozone': 0.3, # atm-cm

    # common gasses
    'carbon_dioxide': 390, # ppm
    'methane': 0.2, # ppm
    'carbon_monoxide': 0, # ppm
    'sulphur_dioxide': 0.01, #ppm
    'nitric_oxide': 0.075, # ppm
    'nitric_acid': 0.001, # ppm
    'nitrogen_dioxide': 0.005, # ppm
    'tropospheric_ozone': 0.0023, # atm-cm

    # SMARTS gasses
    'formaldehyde': 0.001, # ppm
    'nitrous_acid': 0.0005, # ppm
    'nitrogen_trioxide': 1e-5, # ppm

    # SBdart gasses
    'nitrogen': 781000, # ppm
    'oxygen': 209000, # ppm
    'nitrous_oxide': 0.32, # ppm
    'ammonia': 5e-4, # ppm

    'cloud_altitude': 2, # km bottom of cloud ... suggested by QIW
    'cloud_thickness': 1, # km
    'cloud_optical_depth': 0, # optical depth at 0.55 um

    # spectral settings
    'lower_limit': 0.28, # um
    'upper_limit': 2.5, # um
    'resolution': 0.01, # um
}


pollution = {
    # recommended by SMARTS
    'pristine': {
        'formaldehyde': -0.003,
        'methane': 0,
        'carbon_monoxide': -0.1,
        'nitrous_acid': -9.9e-4,
        'nitric_acid': 0,
        'nitric_oxide': 0,
        'nitrogen_dioxide': 0,
        'nitrogen_trioxide': -4.5e-4,
        'tropospheric_ozone': -0.007,
        'sulphur_dioxide': 0,
        },
    'light_pollution': {
        'formaldehyde': 0.001,
        'methane': 0.2,
        'carbon_monoxide': 0,
        'nitrous_acid': 0.0005,
        'nitric_acid': 0.001,
        'nitric_oxide': 0.075,
        'nitrogen_dioxide': 0.005,
        'nitrogen_trioxide': 1e-5,
        'tropospheric_ozone': 0.023,
        'sulphur_dioxide': 0.01,
        },
    'moderate': {
        'formaldehyde': 0.007,
        'methane': 0.3,
        'carbon_monoxide': 0.35,
        'nitrous_acid': 0.002,
        'nitric_acid': 0.005,
        'nitric_oxide': 0.2,
        'nitrogen_dioxide': 0.02,
        'nitrogen_trioxide': 5e-5,
        'tropospheric_ozone': 0.053,
        'sulphur_dioxide': 0.05,
        },
    'severe': {
        'formaldehyde': 0.01,
        'methane': 0.4,
        'carbon_monoxide': 9.9,
        'nitrous_acid': 0.01,
        'nitric_acid': 0.012,
        'nitric_oxide': 0.5,
        'nitrogen_dioxide': 0.2,
        'nitrogen_trioxide': 2e-4,
        'tropospheric_ozone': 0.175,
        'sulphur_dioxide': 0.2,
        },
}