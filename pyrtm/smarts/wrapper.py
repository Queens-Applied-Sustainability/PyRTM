"""
Python wrapper for the SMARTS RTM.
"""
from os import path, remove
import time
import os
import shutil

if __name__ == '__main__':
    import sys
    sys.path.append(path.abspath('../../'))
    from os import chdir
    chdir("../../")
   
from pyrtm.utils import instantiator, popenAndCall
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
                
                'custom': 'USER',
                
                # FIXME ...
                'background stratospheric': 'B&D_C'}


class SMARTS(object):
    """
    Control the SMARTS stuff
    """
    name = 'SMARTS'
    configuration = cards
    
    def __init__(self, config=None):
        super(SMARTS, self).__init__()
        if config is not None:
            self.configuration.update({
                'LATIT': config.latitude,
                'LONGIT': config.longitude,
                'WLMN': config.spectrum.lower_limit,
                'WLMX': config.spectrum.upper_limit,
                'ALTIT': config.surface.altitude,
                'IATMOS': translate.atmosphere[config.atmosphere.profile],
                'AEROS': translate.aerosols[config.aerosols.profile],
            })
            self.output = config.output
         
        #TODO: time needs format: year, month day, hour
        #'YEAR': config.year,
        #'MONTH': config.month,
        #'DAY': config.day,
        #'HOUR': config.hour,
        #'DAY': config.day_of_year,
        #'TIME': config.time,
        #TODO
        #'IOUT': translate.output[config.output],
        #TODO intvl?
        #'wlinc': config.spectrum.resolution,
        #TODO OMEGL?
        #'ISALB': translate.surface[config.surface.albedo_feature],
                
    def writeCards(self):
        infile = open(path.join(WORKING_DIR, INPUT_FILE), 'w')
        infile.write(str(self.configuration))
        infile.close()
    
    def postExec(self):
        print("SMARTS: Cleaning up...")
        output_dir = os.path.join(os.getcwd(), 'data',
                                            'output', self.output, 'SMARTS')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        exe_dir = os.path.join(os.getcwd(), 'pyrtm', 'smarts', 'exe')
        for f in ['log.txt',
                  'smarts295.ext.txt',
                  'smarts295.inp.txt',
                  'smarts295.out.txt']:
            shutil.move(os.path.join(exe_dir, f), os.path.join(output_dir, f))
        tt = time.time() - self.t0
        print("SMARTS: Done (%s) in %f s.\n" % (self.output, tt))
    
    def go(self):
        self.t0 = time.time()
        print('SMARTS: Writing input cards...')
        self.writeCards();
        # run sbdart
        print('SMARTS: Creating subprocess...')
        import subprocess
        exe = path.join(WORKING_DIR, EXECUTABLE)
        popenAndCall(self.postExec, 'echo Y | %s > log.txt' % exe,
                                            shell=True, cwd=WORKING_DIR)
        print('SMARTS: running.')
    
    def __repr__(self):
        return "SMARTS controller. Configuration: %s" % self.configuration


def test_smarts():
    from pyrtm.config import Config
    c = Config()
    s = SMARTS(c)
    s.go()
    
    
if __name__ == '__main__':
    test_smarts()
