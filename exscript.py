from pyrtm import rtm

print "\nTest 1: a single run of SBdart"
sbdart = rtm.SBdart()
myresult = sbdart()
print myresult

print "\nTest 2: ALL THE RTMs"
every_rtm = rtm.All()
all_results = every_rtm()
print all_results
