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


defaults = {
    'description': 'Default Config',
    
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
}
