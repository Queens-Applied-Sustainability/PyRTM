from pyrtm import rtm, utils

def donecallback(results):
    print results[0]

config = utils.RTMConfig({'description': 'Test 1'})

print utils.underline("Test 1: A single run of SBdart", strong=True)
sbdart = rtm.SBdart(config)
sbdart.go(donecallback)

print utils.underline("Test 2: A single run of SMARTS", strong=True)
smarts = rtm.SMARTS(config)
smarts.go(donecallback)

"""
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
