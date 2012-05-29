"""
Python wrapper for the SMARTS RTM.
"""
from os import path, remove 

if __name__ == '__main__':
    import sys
    sys.path.append(path.abspath('../../'))
    from os import chdir
    chdir("../../")
   
from pyrtm.utils import instantiator
from pyrtm.smarts.config import WORKING_DIR, EXECUTABLE, INPUT_FILE, OUTPUT_FILE
from pyrtm.smarts.utils import Card, cards
        
@instantiator
class translate(object):
    atmosphere = {'tropical': 'TRL',
                  'mid-latitude summer': 'MLS',
                  'mid-latitude winter': 'MLW',
                  'sub-arctic summer': 'SAS',
                  'sub-arctic winter': 'SAW',
                  'us62': 'USSA'}
                  
    aerosols = {'rural': 'S&F_RURAL',
                'urban': 'S&F_URBAN',
                'maritime': 'S&F_MARIT',
                'tripospheric': 'S&F_TROPO',
                
                'continental': 'SRA_CONTL',
                'urban': 'SRA_URBAN',
                'maritime': 'SRA_MARIT',
                
                'Braslau & Dave C': 'B&D_C',
                'Braslau & Dave C1': 'B&D_c1',
                
                'desert': 'DESERT_MIN',
                'crazy desert': 'DESERT_MAX',
                
                'custom': 'USER',}


class SMARTS(object):
    """
    Control the SMARTS stuff
    """
    name = 'SMARTS'
    configuration = cards
    
    def __init__(self, config=None, cleanup=True):
        super(SMARTS, self).__init__()
        self.cleanup = cleanup
        if config is not None:
            self.configuration.update({
            })
                
    def writeCards(self):
        pass
        infile = open(path.join(WORKING_DIR, INPUT_FILE), 'w')
        infile.write(str(self.configuration))
        infile.close()
    
    def go(self):
        print('Writing input cards...')
        self.writeCards();
        # run sbdart
        print('Creating SMARTS subprocess...')
        import subprocess
        exe = path.join(WORKING_DIR, EXECUTABLE)
        sbthread = subprocess.Popen('echo Y | ' + exe, shell=True, cwd=WORKING_DIR)
        print('Lookin\' good.')
    
    def __repr__(self):
        return "SMARTS controller. Configuration: %s" % self.configuration

def test_smarts():
    from pyrtm.config import Config
    c = Config()
    s = SMARTS(c)
    s.go()
    
    
if __name__ == '__main__':
    test_smarts()
