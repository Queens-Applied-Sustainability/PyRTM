#!/usr/bin/python
"""
Take a CSV of solar irradiance, and determine which points are clear and
which are cloudy.

Usage: $ python clearfinder.py infile.csv outfile.csv lat lng [options]

Expected CSV columns:

 * Year, month, day, hour, minute, second time information, in columns of
   those names. These will be processed and converted to python datetime
   objects.
 * irradiance, in a column called irrad
 * Any other data columns you wish; they'll be copied over to the new
   sheet without modification.

The output CSV will have the following additional columns:

 * dG (W/m^2 min)
 * kt (ratio of irrad to G0)
 * G0 (W/m^2)
 * clear (bool)

"""

import datetime
from pytz import timezone
from numpy import array, sin, cos, genfromtxt, pi, float64, empty

# RUNNING CONSTANTS -- modify to suit
SKIP_NIGHT = True
NIGHT_CONST = 12 # W/m^2
SOLAR_CONST = 1367 # W/m^2
CHANGE_CONST = 6 # W/m^2 min
Kt_MIN = 0.5
FILE_DELIMITER = ','

# some simple utilities
def dcos(d): return cos(d * pi / 180.) # cos and sin in degrees
def dsin(d): return sin(d * pi / 180.)


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


def find(infile, lat, lng, tz='EST', leaveroom=True):
    """ Given a file of solar data stuff, identify the clear and cloudy
    points. Returns a numpy array with a boolean column 'clear'.
    leaveroom: create columns for AOD and cloud thickness"""
    
    # read in the raw data
    raw = genfromtxt(infile, delimiter=FILE_DELIMITER, names=True,
                     unpack=True, invalid_raise=True)
    
    name_row = raw.dtype.names
    time_cols = ['year','month','day','hour','minute','second']
    data_cols = filter(lambda name: name not in time_cols, name_row)
    
    # Make a list of indices of rows we want to process.
    light_rows = [index for index, row in enumerate(raw)
                  if row['irrad'] > NIGHT_CONST or not SKIP_NIGHT]
    
    # Build the new array
    extra_cols = data_cols + (('AOD', 'cloud', 'err') if leaveroom else ())
    clean = empty(len(light_rows),
        dtype=[
            ('time', datetime.datetime), ('clear', bool),
            ('dG', float64), ('G0', float64), ('kt', float64)
            ] + [(name, float64) for name in extra_cols]
        )
    
    # Set up the timezone
    tzone = {'tzinfo': timezone(tz)}
    
    # process the data
    for clean_num, raw_num in enumerate(light_rows):
        
        # We actually act on the previous row, since we need to use both
        # the forward and backward derivative. raw_num aligns with next.
        last, this, next = clean_num-2, clean_num-1, clean_num
        
        # Convert and save the time (yeah, the "next" row...)
        clean[next]['time'] = datetime.datetime(*[int(raw[raw_num][name])
                                                    for name in time_cols], **tzone)
    
        # Copy the data columns
        for datum in data_cols:
            clean[next][datum] = raw[raw_num][datum]
        
        # Are we past the first row yet?
        if clean_num==0:
            continue # Nothing more to do.
        
        # Calculate the forward derivative
        G, t = clean[this]['irrad'], clean[this]['time']
        Gf, tf = clean[next]['irrad'], clean[next]['time']
        diff_G, diff_t = abs(Gf - G), abs(tf - t)
        delta_G = diff_G / (diff_t.seconds / 60.0) # W/m^2 min
        clean[next]['dG'] = delta_G
        
        # Are we past the second row so we can look at the backward derriv?
        if next == 1:
            continue
        
        # kt n stuff
        clean[this]['G0'] = solar_incident_radiation(t, lat, lng)
        clean[this]['kt'] = G / clean[this]['G0']
        
        # Is it a clear day?
        prev_fast = clean[this]['dG'] > CHANGE_CONST # back deriv
        next_fast = clean[next]['dG'] > CHANGE_CONST # forward deriv
        clean[this]['clear'] = not prev_fast and not next_fast and \
                               clean[this]['kt'] > Kt_MIN
        
    return clean[1:-1] # can't calculate first and last points
    

def clearplot(clean):
    from pylab import plot, show, grid, legend
    dots = {'marker': '.', 'linewidth':0}
    
    plot(clean['time'], clean['G0'], label='G0', color=(0,0,0,0.3))
    plot(clean['time'], clean['G0']*Kt_MIN,
        label='G0*Kt_MIN', color=(0.8,0,0,0.5))
    
    plot(clean['time'], clean['irrad'], color=(0,0,0,0.2))
    plot(*array([(r['time'], r['irrad']) for r in clean if r['clear']]).T,
        label='Clear', color='orange', **dots)
    plot(*array([(r['time'], r['irrad']) for r in clean if not r['clear']]).T,
        label='Cloudy', color='blue', **dots) 
    
    grid()
    legend()
    show()
    

if __name__ == '__main__':
    import sys
    from numpy import save
    # get input/output file names
    try:
        infile, outfile = sys.argv[1:3]
        try:
            lat, lng = map(float, sys.argv[3:5])
        except ValueError:
            sys.stderr.write("  Need a float for lat and lng; got %s and %s\n"
                             % (sys.argv[3], sys.argv[4]))
            sys.exit(1)
    except (ValueError, IndexError):
        sys.stderr.write("  Usage: $ python clearfinder.py infile.csv"\
                         " outfile.csv lat lng\n")
        sys.exit(1)
    
    try:
        clean = find(infile, lat, lng)
    except IOError:
        sys.stderr.write("  Could not read input file %s" % infile)
    
    try:
        save(outfile, clean)
    except IOError:
        sys.stderr.write("  Could not write output file %s" % outfile)
    
    clearplot(clean)
    

