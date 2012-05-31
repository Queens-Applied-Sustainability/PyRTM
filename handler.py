from pyrtm.config import Config
from pyrtm.utils import underline
from pyrtm.sbdart.wrapper import SBDART
from pyrtm.smarts.wrapper import SMARTS
#from pyrtm.rrtm.wrapper import RRTM

#The RTM applications to use:
wrappers = [SBDART, SMARTS]#, RRTM]

print('\n\
  ----------------------------------------- \n\
 |   PYRTM: Radiative Transfer Modelling   |\n\
 |-----------------------------------------|\n\
 | By the Queen\'s University Applied Sus-  |\n\
 | tainability Research Group.             |\n\
 |                                         |\n\
 | Running RMT Modelling scripts:          |\n\
 | %s '                                   '|\n\
  -----------------------------------------\n' %
 ", ".join(wrapper.name for wrapper in wrappers).ljust(39)
 )

print(underline('Setting up'))

print('Loading configuration...')
# TODO update config with input settings
config = Config()#conf=updatesblahblah)
print('Setting up RTM wrappers...')
rtms = [rtm(config) for rtm in wrappers]#, RRMT]]

for rtm in rtms:
    print(underline('Running %s' % rtm.name))
    rtm.go()   

print
#print(underline('Done.'))

