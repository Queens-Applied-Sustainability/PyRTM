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
import csv
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time

import numpy

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
    input_translator = None
    input_generator = None
    output_file = None
    output_extra = []
    output_headers = None
    exe = None
    my_dir = '/home/phil/rtm/PyRTM' # FIXME FIXME FIXME FIXME
    
    def __init__(self, initconfig=None):
        self.log = utils.print_brander(self.name)
        self.result = None
        self.config = utils.RTMConfig(settings.default_config)
        if initconfig:
            self.log("Applying initial configuration.")
            self.config.update(initconfig)
    
    def __call__(self, callback=None, newconfig={}):
        self.callback = callback
        self.config.update(newconfig)
        self.setup_working_dir()
        self._write_input_file()
        #self.log("Done in %#.3gs." % (tf-t0))
        self.run_rtm()
    
    def _write_input_file(self):
        native_config = self.config_translator(self.config)
        rtm_vars = self.input_generator(native_config)
        try:
            infile = open(os.path.join(self.working_dir, self.input_file), 'w')
        except:
            raise self.FileSystemError("Couldn't open input file for writing")
        infile.write(str(rtm_vars))
        infile.close()
    
    def run_rtm(self):
        utils.popenAndCall(self.post_exec, self.exe, shell=True,
                                                    cwd=self.working_dir)
        self.log("Running...")
    
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
        self.log(plain=True) # just a new line
    
    def post_exec(self):
        output_path = os.path.join(self.working_dir, self.output_file)
        self.result = numpy.genfromtxt(output_path,
                                            skip_header=self.output_headers)
        self.clean_up()
        try:
            self.callback(self.result)
        except TypeError:
            pass
    
    def clean_up(self):
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





