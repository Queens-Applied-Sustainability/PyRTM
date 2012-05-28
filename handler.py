from pyrtm.config import Config
from pyrtm.sbdart.wrapper import SBDART
#from pyrtm.smarts.wrapper import SMARTS
#from pyrtm.rrtm.wrapper import RRTM

# TODO update config with input settings
config = Config()#conf=updatesblahblah)



# Register the RTM softwarez
config.register(config, SBDART)
#config.register(SMARTS)
#config.register(RRTM)


def run(config):
    for rtm in config.rtms:
        print('Running %s...' % rtm.name)
        rtm.go()


if __name__ == '__main__':
    run(config)
    
    
    
    
    
    
    
    
    
    
    
    
    

"""
print('Loading default configuration...')
from pyrtm.config import config

print('Loading pyrtm.sbdart...')
from pyrtm.sbdart.wrapper import SBDART
sbdart = SBDART(config, cleanup=False)   #FIXME (cleanup)
print('Executing SBDART!')
sbdart.go()
del(sbdart)
"""
