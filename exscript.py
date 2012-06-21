import pylab
from pyrtm import rtm, utils

config = utils.RTMConfig({
    'description': 'Test 1',
    'time': 17,
})

"""
Parameter                   Default     Unit        SBDART  SMARTS

description                 Hello World string         x      x
year                        2012        year           -      x
day_of_year                 123         days           x      Calc
time                        10.5        hours GMT      x      x
latitude                    44.4        degrees        x      x
longitude                   238.7       degrees        x      x
altitude                    0           km             x      x
height                      0           km             -      x
surface                     vegetation  keywords       x      x
average_daily_temperature   15          deg C          -      x
atmosphere                  mid-latitude summer        x      x
temperature                 15          deg C                 x
pressure                    1013.250    mb             x      x
relative_humidity           35          %              Calc*  x
season                      SUMMER      keywords       -      x
aerosol_optical_depth       0.08                       x      x
angstroms_exponent          1.1977                     x      x
aerosol_asymmetry           0.6         factor         x      x
Solar correction factor     1           factor         auto
Solar constant              1367        w/m^2          -
CO2 concentration           390         ppm            x      x
cloud                       0                          x      -
lower_limit                 0.28        microns        x      x
upper_limit                 2.50        microns        x      x

Zone??



* requires temperature... 

"""


def sbdartcallback(results):
    pylab.plot([result[0] for result in results],
               [result[5] for result in results])
    pylab.draw()

print utils.underline("Test 1: A single run of SBdart", strong=True)
sbdart = rtm.SBdart(config)
sbdart.go(sbdartcallback)


def smartscallback(results):
    pylab.plot([result[0]/1000 for result in results],
               [result[7]*1000 for result in results])
    pylab.show()

print utils.underline("Test 2: A single run of SMARTS", strong=True)
smarts = rtm.SMARTS(config)
smarts.go(smartscallback)





"""
before

precip water (temp(database) and rel humidity(database))
ozone (database)
nitrogen tropospheric [database]
surface pressure [where available]
later -- stratsopheric (smog) [???; not much effect on spectrum -- maybe based on proximity to city]
later -- cloud cover from cloud photos?

iterating on TAERST or DBAER

SMARTS for clear days
SBdart for cloudy days

"""
