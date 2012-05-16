"""Handle the SMARTS stuff

smartsly?
"""

def setup(atm):
    """Create input files for SMARTS
    """
    # Does the input file exist? Then either warn or fail
    
    # Write new input file
    
    # Card 1: Comment
    write_card(vars(atm).get('description', 'Run.')
    
    # Card 2: ISPR Site's pressure.
    if vars(atm).get('surface_pressure'):
        if vars(atm).get('altitude') and vars(atm).get('height'):
            write_card(1)
            # Card 2a: SPR, ALTIT, and HEIGHT
            write_card((atm.surface_pressure, atm.altitude, atm.height))
        else:
            write_card(0)
            # Card 2a: SPR
            write_card(atm.surface_pressure)
    elif vars(atm).get('latitude',) and
         vars(atm).get('altitude') and
         vars(atm).get('height'):
        write_card(2)
        # Card 2a: LATIT, ALTIT, and HEIGHT
        write_card((atm.latitude, atm.altitude, atm.height))
    else:
        # Not enought information!
        raise Exception("SMARTS requires more information for Card 2.")
    
    # Card 3: IATMOS
    if vars.(atm).get('tair') and
       vars(atm).get('relative_humidity') and
       vars(atm).get('season') and
       vars(atm).get('average_daily_temperature'):
        # we have enough info to define a non-reference atmosphere
        write_card(0)
        # Card 3a: Atmos
        write_card((atm.tair, atm.relative_humidity, atm.season,
                                            atm.average_daily_temperature))
    elif vars(atm).get('atmosphere_type'):
        # choose a reference atmosphere
        write_card(1)
        # Card 3a: Atmos
        write_card(atm.atmosphere_type)
    else:
        raise Exception("Not enough atmospheric information for SMARTS")
    
    # Card 4: IH2O
    
    # Card 5: IO3
    
    # Card 6: IGAS
    
    # Card 7: C02 (ppm)
    # Card 7a: ISPCTR
    
    # Card 8: Aeros (aerosol model)
    
    # Card 9: ITURB
    # Card 9a: Turbidity coeff. (TAU5)
    
    # Card 10: IALBDX
    # Card 10b: ITILT
    # Card 10c: Tilt Variables (IALBDG, receiver's tilt & azimuth)
    
    # Card 11: Min & max wavelengths; sun-earth distance correction, solar const
    
    # Card 12: IPRT
    # Card 12a: Min & max wavelengths to print, ideal printing step size
    # Card 12b: Number of variables to Print
    # Card 12c: Variable codes
    
    # Card 13: ICIRC
    # Card 13a: Receiver geometry (3 angles)
    
    # Card 14: ISCAN
    
    # Card 15: ILLUM
    
    # Card 16: IUV
    
    # Card 17: IMASS
    # Card 17a: Air Mass
    
    
    pass

def write_card(line):
    # Check linelength
    pass


def go():
    """Make it run!
    """
    import subprocess
    p = subprocess.Popen('./smarts295', shell=True, stdin=subprocess.PIPE,
                        cwd='exe')
    p.communicate('Y')  # Use stanard mode with default input file?


