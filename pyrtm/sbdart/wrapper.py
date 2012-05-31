"""Python wrapper for the SBDART RTM.

Radiative Transfer Modelling.
Inputs.
Blah blah.
"""

from os import path, remove
import os
import shutil
import time
from pyrtm.utils import FortranNamelist, instantiator, popenAndCall
import pyrtm.utils as utils
from pyrtm.sbdart.config import WORKING_DIR, EXECUTABLE, INPUT_FILE, OUTPUT_FILE

@instantiator
class translate(object):
    output = {'none': 0,
              'per wavelength': 1}
    
    surface = {'snow': 1,
               'clear water': 2,
               'lake water': 3,
               'sea water': 4,
               'sand': 5,
               'vegetation': 6,
               'ocean water': 7}
    
    atmosphere = {'tropical': 1,
                  'mid-latitude summer': 2,
                  'mid-latitude winter': 3,
                  'sub-arctic summer': 4,
                  'sub-arctic winter': 5,
                  'us62': 6}
    
    aerosols = {'no aerosol': 0,
                'background stratospheric': 1,
                'aged volcanic': 2,
                'fresh volcanic': 3,
                'meteor dust': 4}

brander = utils.PrintBrander('SBDART')
log = brander.write

class SBDART(object):
    """Control the SBDART stuff
    """
    name = 'SBDART'
    configuration = FortranNamelist('INPUT')
    
    def __init__(self, config=None, cleanup=True):
        super(SBDART, self).__init__()
        self.cleanup = cleanup
        if config is not None:
            self.configuration.update({
                'ALAT': config.latitude,
                'ALON': config.longitude,
                'IDAY': config.day_of_year,
                'TIME': config.time,
                'IOUT': translate.output[config.output_type],
                'wlinf': config.spectrum.lower_limit,
                'wlsup': config.spectrum.upper_limit,
                'wlinc': config.spectrum.resolution,
                'ISALB': translate.surface[config.surface.albedo_feature],
                'ZPRES': config.surface.altitude,
                'IDATM': translate.atmosphere[config.atmosphere.profile],
                'Zcloud': config.clouds.altitude,
                'Tcloud': config.clouds.optical_thickness,
                'JAER': translate.aerosols[config.aerosols.profile],
            })
            self.output = config.output
                
    def writeNamelistFile(self):
        infile = open(path.join(WORKING_DIR, INPUT_FILE), 'w')
        infile.write(str(self.configuration))
        infile.close()
    
    def postExec(self):
        log("Cleaning up...")
        output_dir = os.path.join(os.getcwd(), 'data',
                                            'output', self.output, 'SBDART')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        exe_dir = os.path.join(os.getcwd(), 'pyrtm', 'sbdart', 'exe')
        for f in ['INPUT', 'OUTPUT', 'SBDART_WARNING.06']:
            try:
                shutil.move(os.path.join(exe_dir, f),
                            os.path.join(output_dir, f))
            except IOError:
                log('not moving file \'%s\'' % f)
        tt = time.time() - self.t0
        log("Done (%s) in %f s.\n" % (self.output, tt))
    
    def go(self):
        self.t0 = time.time()
        log('Writing NAMELIST input file...')
        self.writeNamelistFile();
        # run sbdart
        log('Creating subprocess...')
        exe = path.join(WORKING_DIR, EXECUTABLE) + ' > ' +\
            path.join(WORKING_DIR, OUTPUT_FILE)
        popenAndCall(self.postExec, exe, shell=True, cwd=WORKING_DIR)
        log('running...')
        # clean up
        #if self.cleanup:
        #    remove(path.join(WORKING_DIR, INPUT_FILE))
    
    def __repr__(self):
        return "Fortran controller. Configuration: %s" % self.configuration


