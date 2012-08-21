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

from .. import smarts
from numpy import sin, cos


# cos and sin in degrees
def dcos(d): return cos(d * pi / 180.0)
def dsin(d): return sin(d * pi / 180.0)


def solar_incident_radiation(time, lat, lng):
    """Given a datetime object, latitude, longitude, return the solar
    incident radiation at that moment. So basically what the sun intensity
    is on a plane in space that's parallel to the surface of the earth at
    the specified lat and lng.
    Returns the value in W/m^2.
    From the solar bible thing.
    """
    # Calculate solar time
    standard_time = time
    B = (standard_time.timetuple().tm_yday - 1) * 360.0 / 365.0
    E = 229.2 * (0.000075 + 0.001868 * dcos(B) - 0.032077 * dsin(B) -
                 0.014615 * dcos(2*B) - 0.04089 * dsin(2*B))
    standard_meridian = int(lng/15)*15
    minutes_off = 4*(standard_meridian - lng) + E
    solar_time = standard_time + datetime.timedelta(seconds=minutes_off*60)
    
    tt = solar_time.timetuple()
    year_deg = 360.0 * tt.tm_yday / 365.0
    d = 23.45 * dsin(360.*(284.+tt.tm_yday)/365.) # declination
    phi = lat
    frac_hour = ((tt.tm_hour)+# + tt.tm_isdst) +
                 (tt.tm_min / 60.) +
                 (tt.tm_sec / 60. / 60.))
    omega = (frac_hour - 12) * 15 # hour angle
    cos_theta_z = dcos(phi) * dcos(d) * dcos(omega) + \
                  dsin(phi) * dsin(d)
    fact = (1 + 0.033 * dcos(year_deg)) * cos_theta_z
    G0 = SOLAR_CONST * fact
    
    return G0


def _solve_aod(row):
    

def interpolate():

def _solve_clouds():



def series_solver(station, series, model_columns, pool):

    # series to rows

    clear_rows = [row for row in series if row['clear']]
    clear_dicts = [{var: val} for var, val in zip(row, something) if var in params]
    [row.update(base_config) for row in clear_dicts]

    # solve aods
    aods = pool.map(_solve_aod, clear_dicts)

    # interpolat aods

    blah

    # solve clouds

    return the series























import os
from numpy import trapz, array
from rtm import smarts, sbdart, _rtm
from fmm import zeroin, BadBoundsError, NoConvergeError
import clearfinder

LATITUDE = 44.2
LONGITUDE = -75.3 #284.7

cachedir = False

#from multiprocessing import Pool
#p = Pool(1)
#mapf = p.map
#mapf = map


def rtmcache(model, fn, args):
    runargs = ['description', 'latitude', 'longitude']
    station_string = ' '.join(str(model[v]) for v in runargs)
    global cachedir
    if not cachedir:
        try:
            os.makedirs(os.path.join('rtmcache', station_string))
        except OSError: pass
        cachedir = True
    model_string = ' '.join(str(v) for k, v in model.items()
        if k not in runargs)
    cachefile = os.path.join('rtmcache', station_string, model_string)
    try:
        cached = open(cachefile, 'r').read()
        try:
            return float(cached)
        except ValueError:
            raise BadBoundsError('Could not read cached value')
    except IOError:
        cache = open(cachefile, 'w')
        try:
            result = fn(*args)
        except:
            cache.write('bad (bounds?)')
            cache.close()
            raise
        cache.write(str(result))
        cache.close()
        return result


def solve(index, parameter, lower, upper, tolerance, ref, model):
    modelirrs = []
    diffs = []
    sol = None
    err = 0
    def f(x):
        spectrum = model({parameter: x})
        model_irrad = trapz(spectrum[1], spectrum[0])
        modelirrs.append(model_irrad)
        diff = model_irrad - ref
        diffs.append({x: diff})
        return diff
    try:
        sol = zeroin(lower, upper, f, tolerance)
        #sol = rtmcache(model, zeroin, (lower, upper, f, tolerance))
        print '%d: %s in %d' % (index, str('%s %g' % (model['time'], sol)).ljust(28),
                            len(modelirrs))
    except BadBoundsError as e:
        print 'Bad Bounds at %s: %s; %s' % (model['time'], diffs, e.message)
        err = 1
    except NoConvergeError as e:
        print 'NO CONVERGE'
        err = 2
        #print 'No convergence at %s: %s; %s\ngiven %s' % (model['time'], diffs, e.message, model)
    except _rtm.RTMError as e:
        print 'No output at %s: %s; %s' % (model['time'], diffs, e.message)
        err = 3
        
    return [model['time'], ref, modelirrs, sol, index, err]


def solve_clear_case(case):
    index, time, config, ref = case
    m = smarts.SMARTS(config)
    m.update({'time': time})
    return solve(index, parameter='aerosol_optical_depth',
        lower=0, upper=1, tolerance=0.01, ref=ref, model=m)

def solve_clears(dat, config, mapf):
    cases = [(index, d['time'], config, d['irrad'])
        for index, d in enumerate(dat)if d['clear']]
    aods = mapf(solve_clear_case, cases)
    for aod in aods:
        if not aod[5]:
            dat[aod[4]]['AOD'] = aod[3]
        else:
            dat[aod[4]]['err'] = aod[5]
    return aods


def interpolate_aod(dat):
    lastclear = None
    diff_secs = lambda diff: diff.days*86400 + diff.seconds
    for row, datum in enumerate(dat):
        if datum['AOD'] > 1: # skip rows with invalid aod
            continue
        rtime, val = datum['time'], datum['AOD']
        clear = datum['clear'] and not datum['err']
        prev = dat[row-1] if row else {'time': None}
        pclear = (prev['clear'] and not prev['err']) if row else False
        if clear:
            if not pclear and prev['time'] is not None:
                if lastclear is None:
                    m = 0
                    lastval = val
                    lasttime = rtime
                    lastclear = -1
                else:
                    lasttime = dat[lastclear]['time']
                    lastval = dat[lastclear]['AOD']
                    m = (val - lastval) / diff_secs(rtime - lasttime)
                for cloudrow in range(row-1, lastclear, -1):
                    tdiff = diff_secs(dat[cloudrow]['time'] - lasttime)
                    interp = (tdiff * m) + lastval
                    dat[cloudrow]['AOD'] = interp
            lastclear = row
        if row == len(dat)-1 and not clear: # fill in to the end
            lastval = dat[lastclear]['AOD']
            for cloudrow in range(row, lastclear, -1):
                interp = lastval
                dat[cloudrow]['AOD'] = lastval

    
def solve_cloudy_case(case):
    index, time, config, aod, ref = case
    d = sbdart.SBdart(config)
    d.update({'time': time, 'aerosol_optical_depth': aod})
    return solve(index,
        parameter='cloud', lower=0, upper=30, tolerance=0.01, ref=ref, model=d)

def solve_cloudy(dat, config, mapf):
    cases = [(index, d['time'], config, d['AOD'], d['irrad'])
        for index, d in enumerate(dat) if not d['clear']]
    clouds = mapf(solve_cloudy_case, cases)
    for cloud in clouds:
        dat[cloud[4]]['cloud'] = cloud[3]
    return clouds


if __name__ == '__main__':
    import sys, time
    infile = sys.argv[1]
    print 'reading input'
    dat = clearfinder.find(infile, LATITUDE, LONGITUDE)
    print 'solving'
    try:
        nproc=int(sys.argv[2])
    except:
        pass
    t0 = time.time()
    AODs = solve_clears(dat, nproc if nproc else 1)
    tf = time.time()
    print '%d %g procs time' % (nproc, tf-t0)
    try:
        outfile = sys.argv[3]
        o = open(outfile, 'w')
        o.write(str(AODs))
        o.close()
        print 'done.'
    except:
        print 'error writing file'
    

