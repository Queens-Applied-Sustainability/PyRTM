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

from collections import Iterable
from itertools import repeat
from functools import wraps
import numpy
    

import _rtm
import settings

input_file = 'INPUT'
command = 'sbdart'
header_lines = 3
default_out = 'out.txt'


class SBdartError(_rtm.RTMError): pass


class SBdart(_rtm.Model):
    """
    model some radiative transfers
    """

    def raw(self, rawfile):
        """ grab a raw file """
        with _rtm.Working(self) as working:
            return working.get(rawfile)

    def run(self, output=default_out):
        """ run sbdart """

        with _rtm.Working(self) as working:
            full_cmd = '%s > %s' % (command, output)
            namelist = namelistify(translate(self))
            working.write(input_file, namelist)
            code, err, rcfg = working.run(full_cmd, output)

            if code == 127:
                raise SBdartError('%d: sbdart executable not found. '\
                    'stderr:\n%s' % (code, err))
            elif "error: namelist block $INPUT not found" in err:
                raise SBdartError('sbdart could not read the &INPUT '\
                    'namelist. stderr:\n%s' % err)
            elif code != 0:
                raise SBdartError("sbdart execution failed. Code %d, '\
                    'stderr:\n%s" % (status, err))

    @property
    def spectrum(self):
        """ get the global spectrum for the atmosphere """
        output='out.spectrum.txt'
        self.run(output=output)

        with _rtm.Working(self) as working:
            try:
                sbout = working.get(output)
            except IOError:
                raise SBdartError("didn't get output %s -- %s" %
                    (output, err))
            try:
                model_spectrum = numpy.genfromtxt(
                    sbout, skip_header=header_lines, dtype=[
                        ('wavelength', numpy.float64),
                        ('filter_function_value', numpy.float64),
                        ('top_downward_flux', numpy.float64),
                        ('top_upward_flux', numpy.float64),
                        ('top_direct_downward_flux', numpy.float64),
                        ('global', numpy.float64),
                        ('upward', numpy.float64),
                        ('direct', numpy.float64),
                        ])
            except StopIteration:
                raise SBdartError("Bad output file for genfromtxt (%d header" \
                                  " rows)" % (header_lines))
        
        return model_spectrum

    @property
    def irradiance(self):
        """Get the integrated irradiance across the spectrum"""

        cols = ('top_downward_flux','top_upward_flux',
            'top_direct_downward_flux', 'global',
            'upward', 'direct')

        def get_irrad(col):
            def irrad():
                dat = self.spectrum
                return numpy.trapz(dat[col],dat['wavelength'])
            return irrad

        return _rtm.CallableDict({k: get_irrad(k) for k in cols})


def namelistify(config):
    """convert a dict to a fortran namelist"""
    def fortified(val, first_level=True):
        """Return a variable stringified in a fortran-readable mannor"""
        if isinstance(val, str):
            return "'%s'" % val
        elif isinstance(val, Iterable):
            return ", ".join(fortified(v, False) for v in val)
        else:
            return str(val)
            
    nl = "&INPUT\n"
    nl += "\n".join(" %s = %s" %
                    (key, fortified(val)) for key, val in config.items())
    nl += "\n /\n"
    return nl


def translate(config):
    """
    solar constant

    """
    p = dict(settings.defaults)
    p.update(config)
    
    unsupported = ['description', 'solar_constant', 'season', 'formaldehyde',
        'average_daily_temperature', 'nitrogen_trioxide', 'nitrous_acid']
    
    hard_code = {
        'IAER': 5, # CHANGED TO 5: user set wlbaer, tbaer, wbaer, gbaer
        'JAER': 1, # background stratospheric....
        'WLBAER': 0.55, # um
        'IOUT': 1, # per-wavelength
        'NF': 2, # 2 = lowtran 7
        'ZTRP': 1, # km - assume 1km
        }
    
    direct = {
        'latitude': 'ALAT',
        'longitude': 'ALON',
        'single_scattering_albedo': 'WBAER',
        'aerosol_asymmetry': 'GBAER',
        'pressure': 'PBAR',
        'angstroms_coefficient': 'TBAER', # optical depth at 0.55 um
        'angstroms_exponent': 'ABAER',

        'nitrogen': 'XN2', ##
        'oxygen': 'XO2', ##
        'carbon_dioxide': 'XCO2',
        'methane': 'XCH4',
        'nitrous_oxide': 'XN2O', ##
        'carbon_monoxide': 'XCO',
        'ammonia': 'XNH3', ##
        'sulphur_dioxide': 'XSO2',
        'nitric_oxide': 'XNO',
        'nitric_acid': 'XHNO3',
        'nitrogen_dioxide': 'XNO2',
        'boundary_layer_ozone': 'UO3',
        'tropospheric_ozone': 'O3TRP',

        'lower_limit': 'WLINF',
        'upper_limit': 'WLSUP',
        'resolution': 'WLINC',


        #'strat_aod': 'TAERST',
        #'model': 'NF',
        #'vis': 'VIS',
        #'zbaer': 'ZBAER',
        #'dbaer': 'DBAER',
        }
    
    convert = {
        'time': ((), lambda v:
            (lambda tt: {
                'TIME': tt.tm_hour + tt.tm_min/60.0 + tt.tm_sec/3600.0,
                'IDAY': tt.tm_yday,
                })(v.utctimetuple())
            ),
        'elevation': ((), lambda v: {
            'ZOUT': [v, 50]
            }),
        'surface_type': ((), lambda v: {
            'ISALB': {
                'snow': 1,
                'clear water': 2,
                'lake water': 3,
                'sea water': 4,
                'sand': 5,
                'vegetation': 6,
                'ocean water': 7,
                }[v]
            }),
        'atmosphere': ((), lambda v: {
            'IDATM': {
                'tropical': 1,
                'mid-latitude summer': 2,
                'mid-latitude winter': 3,
                'sub-arctic summer': 4,
                'sub-arctic winter': 5,
                'us62': 6,
                }[v]
            }),
        'temperature': ((), lambda v: {}), # used in the relh calculation
        'relative_humidity': (('temperature',), lambda v: {
            'UW': rh_to_h2o(v, p['temperature'])
            }),
        'cloud_altitude': ((), lambda v: {}), # used in cloud thickness
        'cloud_thickness': (('cloud_altitude',), lambda v: {
            'ZCLOUD': [p['cloud_altitude'], -1 * (p['cloud_altitude'] + v)]
            }),
        'cloud_optical_depth': ((), lambda v: {
            'TCLOUD': [v, 1]
            })
        }
    
    processed = []
    translated = {}
    translated.update(hard_code)
    
    def addItem(param, val):
        if param not in unsupported:
            if param in direct:
                translated.update({direct[param]: val})
            elif param in convert:
                [addItem(d) for d in convert[param][0] if not d in processed]
                translated.update(convert[param][1](val))
            else:
                print "x %s" % param # Unrecognized!
            
        processed.append(param)
    
    for param, val in p.items():
        if param not in processed:
            addItem(param,val)
    
    return translated


def rh_to_h2o(rel_humid, temp):
    """Saturation vapour pressure (mb). C. Gueymard, Assessment of the
    Accuracy and Computing Speed of Simplified Saturation Vapor Equations
    Using a New Reference Dataset, J. Appl. Meteor. 32 (1993) 1294-1300.
    Input is in degrees C and % RH"""
    RH = rel_humid
    T = temp
    pws = (6.110455 +
           (0.4440371 * T) +
           (1.430201E-2 * numpy.power(T, 2)) +
           (2.652469E-4 * numpy.power(T, 3)) +
           (3.03571E-6 * numpy.power(T, 4)) +
           (2.036766E-8 * numpy.power(T, 5)) -
           (1.469687E-13 * numpy.power(T, 6)))
    #saturation vapour density
    rho_v = 216.7 * RH * pws / 100 / (T+273)
    theta = (T + 273.15) / 273.15
    #water vapour scale height
    H_v = (0.4976 + 1.5265 * theta +
           numpy.exp(13.6897 * theta-14.9188 * numpy.power(theta, 3)))
    #preciptable water (cm)
    w = 0.1 * H_v * rho_v
    return w


