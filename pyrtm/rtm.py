"""Set up configuration for a run

The atmospheric settings here are blah blah blah
"""

class configuration(object):
    description = "Example Run"
    
    class solar(object):
        pass
        # most of this can be calculated from latitude & day/time
    
    class atmosphere(object):
        
        

meta = {
    description: "Example Run",  # max 64 chars             # SMARTS
    # Date and time?!
    
    solar {
        zenith_angle: None,                                 # SBDART
        # sbdart csza -- cosine of solar zenith angle
    }
    
    sensor: {
        altitude: None,                                     # SMARTS
        height: None,                                       # SMARTS
        latitude: None,                                     # SMARTS
    }

    atmosphere: {
        atmospheric_profile: "sub_arctic_summer",           # SBDART
        surface_pressure: None,                             # SMARTS
        # SBDART can handle up to 5 cloud layers
        clouds: [
            {
                optical_thickness: 10
                drop_radius: 10, # microns
                altitude: 8,
            },
        ],
        # sbdart amix -- weighting factor for different atmospheres
    }
    
    # sbdart isat -- filter function types (gaussian, triangular, flat,
    # defined from filter.dat
    
    # sbdart wlinf -- lower wavelength limit when isat=0; central isat=-2,-3,-4
    # sbdart wlsup
    # sbdart wlinc
    
    
    # sbart solfac -- solar distance factor (account for seasonal variation)
    
    # sbdart nf -- solar spectrum selector
    
}


