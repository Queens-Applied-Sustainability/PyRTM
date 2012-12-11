"""tools for sun stuff"""

import datetime
from numpy import sin, cos, pi


SOLAR_CONST = 1367 # W/m^2


def dcos(d): return cos(d * pi / 180.) # cos and sin in degrees
def dsin(d): return sin(d * pi / 180.)

def extraterrestrial_radiation(time, lat, lng):
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
    standard_meridian = int((((360 - lng) + 360) % 360) / 15) * 15
    minutes_off = 4*(standard_meridian - (360 - lng)) + E
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

# DEPRECTATED FUNCTION NAME
# incident_radiation will be removed soon
def incident_radiation(*args, **kwargs):
    print("WARNING: this function is deprecated, please use extraterrestrial_radiation instead.")
    return extraterrestrial_radiation(*args, **kwargs)