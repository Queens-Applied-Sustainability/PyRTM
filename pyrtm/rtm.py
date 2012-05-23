"""Set up configuration for a run

The atmospheric settings here are blah blah blah
"""
     
#   self.description = None  # Note: SMARTS trucates at 64 chars

#self.surface_pressure = None

#self.altitude = None
#self.latitude = None
#self.height = None
    
   
atmosphere = {
    description: "Example run",                         # SMARTS
    solar_zenith_angle: None,                           # SBDART
    atmospheric_profile: "sub_arctic_summer",           # SBDART
    # SBDART can handle up to 5 cloud layers
    clouds: [
        {
            optical_thickness: 10
            drop_radius: 10, # microns
            altitude: 8,
        },
    ],
}
