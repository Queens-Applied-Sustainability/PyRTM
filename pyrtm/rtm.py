"""
    Copyright (c) 2012 Philip Schliehauf (uniphil@gmail.com) and the
    Queen's University Applied Sustainability Centre
    
    This project is hosted on github; for up-to-date code and contacts:
    https://github.com/Queens-Applied-Sustainability/PyRTM
    
    This file is part of PyRTM.

    PyRTM is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyRTM is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyRTM.  If not, see <http://www.gnu.org/licenses/>.
"""

import abc
import os
import shutil
import tempfile
import time

import utils
import settings


class _RTM(object):
    """
    Abstract class describing interactions with RTM applications.
    """
    __metaclass__ = abc.ABCMeta
    
    name = None
    executable = None
    bin_path = None
    resources = []
    input_file = None
    output_file = None
    output_extra = []
    my_dir = '/home/phil/rtm/PyRTM' # FIXME FIXME FIXME FIXME
    
    def __init__(self, initconfig=None):
        #self.t0i = time.time()
        self.log = utils.print_brander(self.name)
        self.log("Loading default configuration.")
        self.config = utils.RTMConfig(settings.default_config)
        if initconfig:
            self.log("Applying initial configuration.")
            self.config.update(initconfig)
    
    def __call__(self, newconfig={}):
        #t0c = time.time()
        self.config.update(newconfig)
        self.setup_working_dir()
        self._write_input_file(self.rtm_vars)
        #t0e = time.time()
        self.log("Running...")
        t0 = time.time()
        result = self.run_rtm()
        tf = time.time()
        self.log("Done in %3fs." % (tf-t0))
        #tf = time.time()
        #self.log("Times since init, call, exec: %s" %
        #            ", ".join("%2fs" % (tf-t)  for t in (self.t0i, t0c, t0e)))
        self.clean_up()
        return result
    
    def _write_input_file(self, rtm_vars):
        #rtm_vars = None
        try:
            in_file = open(os.path.join(self.working_dir, self.input_file), 'w')
        except:
            raise self.FileSystemError("Couldn't open input file for writing")
        in_file.write(str(rtm_vars))
        in_file.close()
    
    @property
    @abc.abstractmethod
    def rtm_vars(self): pass
    
    @abc.abstractmethod
    def run_rtm(self): return
    
    def setup_working_dir(self):
        self.working_dir = tempfile.mkdtemp(suffix=self.name)
        # symbolically link to the executable and resources
        self.log("Linking: ", no_break=True)
        for resource in [self.executable] + self.resources:
            try:
                self.log("%s" % resource, plain=True, no_break=True)
                os.symlink(os.path.join(self.my_dir, self.bin_path, resource),
                           os.path.join(self.working_dir, resource))
            except OSError:
                raise self.FileSystemError("Huh. Can't make some symlinks "\
                                           "that I need in order to work. "\
                                           "Maybe in a future version I'll "\
                                           "be SMARTS enough to fall back to "\
                                           "something sensible...")
        self.log(plain=True)
    
    def clean_up(self):
        try:
            shutil.rmtree(self.working_dir)
        except NameError:
            self.log("Nothing to clean -- was it ever created?")
        except OSError:
            self.log("Can't remove the directory. Does it exist? Do we have "\
                     "permission?")
        else:
            self.log("Successfully cleaned up temporary files.")
    
    class FileSystemError(Exception): pass


class SMARTS(_RTM):
    name = 'SMARTS'
    bin_path = os.path.join('bin', 'smarts')
    executable = 'smarts295'
    resources = ['Albedo', 'CIE_data', 'Gasses', 'Solar']
    input_file = 'smarts295.inp.txt'
    output_file = 'smarts295.out.txt'
    
    def write_input_file(self):
        return # FIXME
    def run_rtm(self):
        return # FIXME


class SBdart(_RTM):
    name = 'SBdart'
    bin_path = os.path.join('bin', 'sbdart')
    executable = 'drtx'
    input_file = 'INPUT'
    output_file = 'OUTPUT'
    
    _translate = settings.translate('SBdart') # returns a dict
    
    def rtm_vars(self):
        return utils.Namelist('INPUT', {
            'ALAT': self.config['latitude'],
            'ALON': self.config['longitude'],
            'IDAY': self.config['day of year'],
            'TIME': self.config['time'],
            #'IOUT': self._translate['output'][self.config['output']], #FIXME
            'wlinf': self.config['lower limit'],
            'wlsup': self.config['upper limit'],
            'wlinc': self.config['resolution'],
            'ISALB': self._translate['surface'][self.config['surface albedo']],
            'ZPRES': self.config['surface elevation'],
            'IDATM': self._translate['atmosphere'][self.config['atmosphere']],
            'Zcloud': self.config['cloud altitude'],
            'Tcloud': self.config['cloud optical depth'],
            'JAER': self._translate['aerosols'][self.config['aerosols']],
        })
        
    def run_rtm(self):
        exe = '%s > %s' % (os.path.join(self.working_dir, self.executable),
                           os.path.join(self.working_dir, self.output_file))
        #utils.popenAndCall(self.blah, exe, shell=True, cwd=self.exe_path)


def All(*args, **kwargs):
    """
    Return an EachList containing all the RTM wrappers.
    
    Check out utils.EachList and the corresponding unit tests for more on how
    EachLists work.
    
    You can use this just like you'd use the RTM classes; everything will be
    the same except that all the results will be elements of an EachList.
    """
    return utils.EachList([SMARTS, SBdart])(*args, **kwargs)





