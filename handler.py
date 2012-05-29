from pyrtm.config import Config
from pyrtm.sbdart.wrapper import SBDART
#from pyrtm.smarts.wrapper import SMARTS
#from pyrtm.rrtm.wrapper import RRTM


print('Loading configuration...')
# TODO update config with input settings
config = Config()#conf=updatesblahblah)

print('Setting up RTM wrappers...')
rtms = [rtm(config) for rtm in [SBDART]]#, SMARTS, RRMT]]

for rtm in rtms:
    print('Running %s...' % rtm.name)
    rtm.go()   


