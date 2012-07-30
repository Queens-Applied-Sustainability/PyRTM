	READ ME -- Example 3-UV_reference_spectra

This example shows how to generate a reference UV spectrum that matches the 
atmospheric conditions also used in older terrestrial solar irradiance 
standards (ASTM E891-87, ASTM E892-87, ASTM G159-99; ISO 9845-1). 
See Example 6 to approximate the more recent ASTM G173 spectra, and Example 10 to 
approximate the UV spectrum defined by ASTM G177.

SMARTS2 will be run here from 280 to 400 nm, and the optional broadband-UV 
calculations will be added for demonstration purposes.

As also explained in Example 1, these standards specify an air mass of 1.5, 
a rural aerosol with  optical thickness of 0.27 at 500 nm, a US Standard 
Atmosphere with 1.42 cm precipitable water and 0.34 atm-cm ozone, a fixed 
broadband albedo of 0.2, and circumsolar radiation within a cone of about 
2.9 deg. half angle. 
These conditions are used here in the first run. A second run is added with 
identical conditions, except for an air mass of 1.2.

The differences with Example 1 are the wavelength limits (see above), the 
output wavelength interval (0.5 nm in the present case), the request for 2 
successive runs here (instead of 1 in Example 1), and the request for UV 
specific calculations here (instead of the illuminance specific calculations in 
Example 1).
