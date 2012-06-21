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
import numpy
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time

import settings
import utils


class _RTM(dict):
    """
    Abstract class describing interactions with RTM applications.
    """
    __metaclass__ = abc.ABCMeta
    
    name = None         # How shall I identify myself?
    executable = None   # What is my executable called?
    bin_path = None     # What is the path to my binary folder?
    resources = []      # What other important items are in my binary folder?
    input_file = None   # What is the name of the file I read for input?
    input_translator = None # Who can I call to get the config in my language?
    input_generator = None  # Who can format the config into something I read?
    output_file = None  # To where shall/do I write my output?
    output_extra = []   # What other extra files do I write?
    output_headers = None   # How many garbage lines to I produce?
    exe = None          # What command makes me go?
    my_dir = '/home/phil/PyRTM' # FIXME FIXME FIXME FIXME ugly ugly ugly
    clean_after = True  # Shall I erase the temporary directory I created? 
    
    def __init__(self, d={}, *args, **kwargs):
        """
        Create default configuration and set up logger.
        
        Accepts configuration parameters passed as a dictionary.
        """
        default_d = utils.RTMConfig(settings.default_config)
        default_d.update(d)
        super(_RTM, self).__init__(default_d, *args, **kwargs)
        self.result = None
        self.log = utils.print_brander(self.name + " " + self['description'])
    
    def _write_input_file(self):
        native_config = self.config_translator(self)
        rtm_vars = self.input_generator(native_config)
        try:
            infile = open(os.path.join(self.working_dir, self.input_file), 'w')
        except:
            raise self.FileSystemError("Couldn't open input file for writing")
        infile.write(str(rtm_vars))
        infile.close()
    
    def setup_working_dir(self):
        self.working_dir = tempfile.mkdtemp(suffix=self.name)
        # symbolically link to the executable and resources
        self.log("Linking", no_break=True)
        for resource in [self.executable] + self.resources:
            try:
                self.log("%s" % resource, plain=True, no_break=True)
                os.symlink(os.path.join(self.my_dir, self.bin_path, resource),
                           os.path.join(self.working_dir, resource))
            except OSError:
                raise self.FileSystemError("Huh. Can't make some symlinks "\
                    "that I need in order to work. Maybe in a future version "\
                    "I'll be SMARTS enough to fall back to something...")
        self.log(plain=True) # clear the line \n
    
    def go(self, callback=None, newconfig={}):
        self.callback = callback
        self.update(newconfig)
        self.setup_working_dir()
        self._write_input_file()
        self._t0 = time.time()
        utils.popenAndCall(self.post_exec, self.exe, shell=True,
                                                    cwd=self.working_dir)
        self.log("Running...")
    
    def get(self, newconfig = {}):
        self.update(newconfig)
        self.setup_working_dir()
        self._write_input_file()
        self._t0 = time.time()
        proc = subprocess.Popen(self.exe, shell=True, cwd=self.working_dir)
        proc.wait()
        self.t = time.time() - self._t0
        self.log("Done in %#.3gs." % self.t)
        self.read_output()
        self.clean_up()
        return self.result
    
    def post_exec(self):
        self.t = time.time() - self._t0
        self.log("Done in %#.3gs." % self.t)
        self.read_output()
        self.clean_up()
        try: 
            self.callback(self.result)
        except TypeError:
            pass
    
    def read_output(self):
        output_path = os.path.join(self.working_dir, self.output_file)
        try:
            rtm_result = numpy.genfromtxt(
                            output_path, skip_header=self.output_headers)
        except StopIteration:
            raise self.FileSystemError("Something went wrong reading output!")
        else:
            self.result = {'description': self['description'],
                           'result': rtm_result}
    
    def clean_up(self):
        if self.clean_after:
            try:
                shutil.rmtree(self.working_dir)
            except NameError:
                self.log("Nothing to clean -- was it ever created?")
            except OSError:
                self.log("Can't remove the directory. Does it exist? Permission?")
            else:
                self.log("Successfully cleaned up temporary files.")
    
    class FileSystemError(Exception): pass


class SMARTS(_RTM):
    name = 'SMARTS'
    bin_path = os.path.join('bin', 'smarts')
    executable = 'smarts295'
    resources = ['Albedo', 'CIE_data', 'Gases', 'Solar']
    input_file = 'smarts295.inp.txt'
    config_translator = settings.translate_smarts
    input_generator = utils.smarts_cards
    output_file = 'smarts295.ext.txt'
    output_headers = 1
    output_extra = ['log.txt', 'smarts295.out.txt']
    exe = './%s > log.txt' % executable


class SBdart(_RTM):
    name = 'SBdart'
    bin_path = os.path.join('bin', 'sbdart')
    executable = 'drtx'
    input_file = 'INPUT'
    config_translator = settings.translate_sbdart
    input_generator = utils.Namelist('INPUT')
    output_file = 'OUTPUT'
    output_headers = 3
    exe = './%s > %s' % (executable, output_file)
    
    def read_output(self):
        files = os.listdir(self.working_dir)
        for warning in (w for w in files if re.match(r'^SBDART_WARNING.', w)):
            try:
                warn_file = open(os.path.join(self.working_dir, warning), 'r')
            except IOError:
                self.log(warning)
            else:
                self.log(warn_file.readline(), no_break=True) # has break
                warn_file.close()
        
        return _RTM.read_output(self)


def All(*args, **kwargs):
    """
    Return an EachList containing all the RTM wrappers.
    
    Check out utils.EachList and the corresponding unit tests for more on how
    EachLists work.
    
    You can use this just like you'd use the RTM classes; everything will be
    the same except that all the results will be elements of an EachList.
    """
    return utils.EachList([SMARTS, SBdart])(*args, **kwargs)





