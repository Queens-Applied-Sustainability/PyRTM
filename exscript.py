import pylab

from pyrtm import rtm, utils

config = utils.RTMConfig({
    'description': 'Test 1'
})

"""
Parameter                   Default     Unit        SBDART  SMARTS

description                 Hello World string        x       x
year                        2012        year          -       x
day_of_year                 123         days          x       Calc
time                        10.5        dec. hours    x       x
latitude                    44.4        degrees       x       x
longitude                   238.7       degrees       x       x
altitude                    0           km            x       x
height                      0           km            -       x
average_daily_temperature   15          deg C         -       x
temperature                             deg C         
relative_humidity           35          %             Calc    x
season                      SUMMER      keywords      -       x
angstroms_exponent_low      1.4                       -       x
angstroms_exponent_high     1.4                       -       x
Omegl?
GG?
Beta?!!!
Albedo                                  keywords      x       x
lower_limit                 0.28        microns
upper_limit                 2.50        microns
Solar correction factor     1           
Solar constant              1367
CO2 concentration           390

Year??
Zone??



"""

""" """
def sbdartcallback(results):
    pylab.plot([result[0] for result in results],
               [result[5] for result in results])
    pylab.show()

print utils.underline("Test 1: A single run of SBdart", strong=True)
sbdart = rtm.SBdart(config)
sbdart.go(sbdartcallback)

""" """
def smartscallback(results):
    pylab.plot([result[0]/1000 for result in results],
               [result[1]*1000 for result in results])
    pylab.show()

print utils.underline("Test 2: A single run of SMARTS", strong=True)
smarts = rtm.SMARTS(config)
smarts.go(smartscallback)


""" " ""
print utils.underline("Test 3: ALL THE rtms", strong=True)
every_rtm = rtm.All(run="Test 3")
every_rtm(donecallback)
"""







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
