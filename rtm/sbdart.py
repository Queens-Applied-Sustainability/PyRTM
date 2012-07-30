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
import numpy
    

import _rtm
import settings

input_file = 'INPUT'
command = 'sbdart'
output_file = 'OUTPUT'
header_lines = 3

class SBdartError(_rtm.RTMError): pass

def sbdart(atm={}, cleanup=True):
    myatm = dict(atm)
    def runner(atm={}):
        myatm.update(atm)
        with _rtm.Working(cleanup=cleanup) as working:
            working.write(input_file, namelistify(translate(myatm)))
            
            code, err = working.run('%s > %s' % (command, output_file))
            if code == 127:
                raise SBdartError("%d: sbdart Executable not found. Did you"\
                    " install it correctly? stderr:\n%s" % (code, err))
            elif "error: namelist block $INPUT not found" in err:
                raise SBdartError("sbdart couln't read the &INPUT block."\
                    " stderr:\n%s" % err)
            elif code != 0:
                raise SBdartError("Execution failed with code %d. stderr:\n%s"
                    % (status, err))
            
            sbout = working.get(output_file)
            try:
                raw = numpy.genfromtxt(sbout, skip_header=header_lines)
            except StopIteration:
                raise SBdartError("Bad output file for genfromtxt (%d header" \
                                  " rows)." % header_lines)
            return numpy.array([raw[:,0], raw[:,5]])
    return runner

def picklable(atm={}, *args, **kwargs):
    d = sbdart(*args, **kwargs)
    return d(atm)


def namelistify(params):
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
                    (key, fortified(val)) for key, val in params.items())
    nl += "\n /\n"
    return nl


def translate(params):
    p = dict(settings.defaults)
    p.update(params)
    
    unsupported = ['description', 'temprerature', 'solar_constant',
                   'season', 'year', 'average_daily_temperature',
                   'temperature', 'single_scattering_albedo',
                   'angstroms_exponent', 'aerosol_asymmetry', 'output']
    
    hard_code = {
        'IAER': 1,
        'ZCLOUD': 6,
        'IOUT': 1, # per-wavelength
        }
    
    direct = {
        'latitude': 'ALAT',
        'longitude': 'ALON',
        'day_of_year': 'IDAY',
        'time': 'TIME',
        'pressure': 'PBAR',
        'carbon_dioxide': 'XCO2',
        'aerosol_optical_depth': 'TBAER',
        'cloud': 'TCLOUD',
        'lower_limit': 'WLINF',
        'upper_limit': 'WLSUP',
        'resolution': 'WLINC',
        }
    
    convert = {
        'altitude': ((), lambda v: {
            'ZOUT': [v, 50]
            }),
        'surface': ((), lambda v: {
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
        'relative_humidity': (('temperature',), lambda v: {
            'UW': rh_to_h2o(v, p['temperature'])
            }),
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
                print "x %s" % param # ERROR!
            
        processed.append(param)
    
    for param, val in p.items():
        if param not in processed:
            addItem(param,val)
    
    return translated


def rh_to_h2o(rel_humid, temp):
    """Saturation vapour pressure (mb). C. Gueymard, Assessment of the
    Accuracy and Computing Speed of Simplified Saturation Vapor Equations
    Using a New Reference Dataset, J. Appl. Meteor. 32 (1993) 1294-1300."""
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


