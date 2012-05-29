"""Python wrapper for the SMARTS RTM.

Radiative Transfer Modelling.
Inputs.
Blah blah.
"""

from os import path, remove
from pyrtm.utils import instantiator
from pyrtm.smarts.config import WORKING_DIR, EXECUTABLE, INPUT_FILE, OUTPUT_FILE
from pyrtm.smarts.utils import SmartsCards

@instantiator
class translate(object):
    pass

class SMARTS(object):
    """Control the SMARTS stuff
    """
    name = 'SMARTS'
    configuration = SmartsCards()
    
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


