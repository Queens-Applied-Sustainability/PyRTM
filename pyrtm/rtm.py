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
        self.log = utils.print_brander(self.name)
        self.log("Loading default configuration.")
        self.config = utils.RTMConfig(settings.default_config)
        if initconfig:
            self.log("Applying initial configuration.")
            self.config.update(initconfig)
    
    def __call__(self, newconfig={}):
        self.setup_working_dir()
        self.config.update(newconfig)
        self.write_input_file()
        result = self.run_rtm()
        self.clean_up()
        return result
    
    @abc.abstractmethod
    def write_input_file(self):
        return
    
    @abc.abstractmethod
    def run_rtm(self):
        returns
    
    def setup_working_dir(self):
        """
        working = os.path.join('/tmp/pyrtm', self.name) # FIXME FIXME FIXME
        try: # use /tmp
            self.log("trying to create /tmp...")
            os.makedirs(working)
        except OSError: # can't create /tmp!
            if os.path.exists(working):
                self.log("Whoa! Working directory colission?! I'm going to "\
                         "be rude and erase everything to use it myself.")
                try:
                    shutil.rmtree(working)
                except OSError:
                    raise self.FileSystemError("Sorry, I just can't run "\
                                               "these conditions!")
                else:
                    try:
                        os.makedirs(working)
                    except:
                        raise self.FileSystemError("oh give me a break. is "\
                                                   "this case necessary?!")
            else:
                raise self.FileSystemError("Oops -- you don't have a /tmp "\
                                           "directory on your computer and "\
                                           "I'm not smart enough to figure "\
                                           "out another place to use instead.")
        self.working_dir = working
        """
        self.working_dir = tempfile.mkdtemp(suffix=self.name)
        # symbolically link to the executable and resources
        for resource in [self.executable] + self.resources:
            try:
                self.log("linking in '%s'" % resource)
                os.symlink(os.path.join(self.my_dir, self.bin_path, resource),
                           os.path.join(self.working_dir, resource))
            except OSError:
                raise self.FileSystemError("Huh. Can't make some symlinks "\
                                           "that I need in order to work. "\
                                           "Maybe in a future version I'll "\
                                           "be SMARTS enough to fall back to "\
                                           "something sensible...")
    
    def clean_up(self):
        try:
            shutil.rmtree(self.working_dir)
        except NameError:
            self.log("Nothing to clean -- was it ever created?")
        except OSError:
            self.log("Can't remove the directory. Does it exist? Do we have "\
                     "permission?")
        else:
            self.log("Successfully cleaned up temporaries")
    
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
    
    def write_input_file(self):
        rtm_vars = utils.Namelist('INPUT', {
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
        in_file = open(os.path.join(self.working_dir, self.input_file), 'w')
        in_file.write(str(rtm_vars))
        in_file.close()
    
    def blah(self):
        print "blah"
        
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





