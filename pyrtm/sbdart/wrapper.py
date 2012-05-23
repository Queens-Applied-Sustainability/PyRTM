"""Python wrapper for the SBDART RTM.

Radiative Transfer Modelling.
Inputs.
Blah blah.
"""

from os import path, remove
from pyrtm.futils import FortranNamelist
from pyrtm.sbdart.config import WORKING_DIR, EXECUTABLE, INPUT_FILE, OUTPUT_FILE

class SBDART:
    """Control the SBDART stuff
    """
    atmosphere = FortranNamelist('INPUT')
    
    def __init__(self, cleanup=True, atm=None):
        self.cleanup = cleanup
        if atm is not None:
            # set up our atmosphere
            pass
        
    def writeNamelistFile(self):
        infile = open(path.join(WORKING_DIR, INPUT_FILE), 'w')
        infile.write(str(self.atmosphere))
        infile.close()
        print('wrote input file.')
    
    def go(self):
        self.writeNamelistFile();
        # run sbdart
        import subprocess
        exe = path.join(WORKING_DIR, EXECUTABLE) + ' > ' +\
            path.join(WORKING_DIR, OUTPUT_FILE)
        sbthread = subprocess.Popen(exe, shell=True, cwd=WORKING_DIR)
        # clean up
        if self.cleanup:
            remove(path.join(WORKING_DIR, INPUT_FILE))
    
    def __repr__(self):
        return "Fortran controller. Atmosphere:\n" + str(self.atmosphere)


