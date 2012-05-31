from utils import config_meta, group_property, instantiator, Conf

class Config(Conf):
    __metaclass__ = config_meta
    
    description = 'hello world'
    output = 'default'
    output_type = 'per wavelength'
    
    day_of_year = 103
    time = 18.8333 # GMT decimal hours
    latitude = 44
    longitude = 283.7
    
    
    class spectrum(Conf):
        selector = 'lowtran 7'                          # SBDART default
        filter_function_type = 0 #FIXME: human-readable values  # SBDART Default
        resolution = 0
        lower_limit = 0.25
        upper_limit = 2.5

        @group_property
        def central(conf):
            return conf.spectrum.wavelength.lower_limit

        @group_property
        def width(conf):
            return conf.spectrum.wavelength.upper_limit

    class solar(Conf):
        zenith_angle = 0
        
        @group_property
        def azimuth_angle(conf):
            return 90 - conf.solar.zenith_angle
    
    class atmosphere(Conf):
        profile = 'mid-latitude summer'
        
    class clouds(Conf):
        altitude = [0, 0, 0, 0, 0]
        optical_thickness = [0, 0, 0, 0, 0]
        
    class aerosols(Conf):
        profile = 'background stratospheric'
    
    class surface(Conf):
        albedo_feature = 'vegetation'
        altitude = 0.11 #km

