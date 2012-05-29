
class SmartsCards(dict):
    array_delimiter = " " # can be a space or a comma
    
    """
    mandatory fields:
    
    1 COMNT - comment - 64 char truncate
    
    2 ISPR - site's pressure - 0, 1, or 2 for different modes
        a - surface pressure (ISPR == 0)
        a - surface pressure, altitude, height (ISPR == 1)
        a - lat, alt, height (ISPR == 2)
    
    3 IATMOS - default atmosphere - 0 or 1 for modes
        a - tair, rh, season, tday (IATMOS == 0)
        a - atmos (IATMOS == 1)
    
    4 IH2O - precipitable water - 0, 1, or 2 for modes
        a - precipitable water (IH2O == 0) - above the site altitude in cm
    
    5 IO3 - Ozone abundance input - 0 or 1 for modes
        a - IALT, AbO3 (IO3 == 0)
        
    6 IGAS - Gaseous absorption - 0 or 1 for modes
        a - ILOAD (IGAS == 0)
            b - ApCH20, ApCh4 ,........ (ILOAD == 0)
    
    7 qCO2 - CO2 Concentration
    
    7a ISPCTR - Extraterrestrial spectrum - -1, 0..8 for different data inputs
    
    8 AEROS - Aerosol model
        a - ALPHA1, ALPHA2, OMEGL, GG (AEROS == 'USER')
    
    9 ITURB - Turbidity input - 0..5
        a TAU5 (ITURB == 0)
        a BETA (ITURB == 1)
        a BCHUEP (ITURB == 2)
        a RANGE (ITURB == 3)
        a VISI (ITURB == 4)
        a TAU550 (ITURB == 5)
        
    10 IALBDX - Zonal albedo - -1..2, many more
        a RHOX (IALBDX == -1)
        
    10b ITILT - Tilted surface 0 or 1
        c IALBDG, TILT, WAZIM (ITLIT == 1)
        
    11 WLMN, WLMX, SUNCOR, SOLARC - spectral range, correction factor, solar const
    
    12 IPRT - printing options - 0, 1, 2, 3
        a WPMN, WPMX, INTVL (IPRT >= 1)
            b IOTOT (IPRT == 2 or 3)
                c IOUT (IPRT == 2 or 3), 1..43
                
    13 ICIRC - Circumsolar radiation, 0 or 1 modes
        a SLOPE, APERT, LIMIT (ICIRC == 1)
    
    14 ISCAN - Scanning/smoothing filter 0 or 1
        a IFILT, WV1, WV2, STEP, FWHM (ISCAN == 1)
    
    15 ILLUM - Illuminance -1, 1, -2, 2, or 0 (bypass)
    
    16 IUV - Special UV Calcs, 0=none, 1=do it
    
    17 IMASS - Solar position and air mass calcs 0..4 modes
        a 0 ZENIT, AZIM
        a 1 ELEV, AZIM
        a 2 AMASS
        a 3 YEAR, MONTH, DAY, HOUR, LATIT, LONGIT, ZONE <- probably
        a 4 MONTH, LATIT, DSTEP
        
    """
    
    def __str__(self):
        return """'Example_6:USSA_AOD=0.084'		  !Card 1 Comment
1			!Card 2 ISPR
1013.25 0. 0.		!Card 2a Pressure, altitude, height
1			!Card 3 IATMOS
'USSA'			!Card 3a Atmos
1			!Card 4 IH2O
1			!Card 5 IO3
1			!Card 6 IGAS
370.0			!Card 7 CO2 amount (ppm)
1			!Card 7a ISPCTR
'S&F_RURAL'		!Card 8 Aeros (aerosol model)
0			!Card 9 ITURB
0.084			!Card 9a Turbidity coeff. (TAU5)
38			!Card 10 IALBDX
1			!Card 10b ITILT
38 37. 180.			!Card 10c Tilt variables (IALBDG, receiver's tilt & azimuth)
280 4000 1.0 1367.0		!Card 11 Min & max wavelengths; sun-earth distance correction; solar constant
2			!Card 12 IPRT
280 4000 .5		!Card12a Min & max wavelengths to be printed; ideal printing step size
4			!Card12b Number of Variables to Print
8 9 10 30			!Card12c Variable codes
1			!Card 13 ICIRC
0 2.9 0			!Card 13a Receiver geometry (3 angles)
0			!Card 14 ISCAN
0			!Card 15 ILLUM
0			!Card 16 IUV
2			!Card 17 IMASS
1.5			!Card 17a Air mass
"""
    
    def __repr__(self):
        return super(SmartCards, self).__repr__()
