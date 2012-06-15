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
        self.config.update(newconfig)
        self.setup_working_dir()
        self._write_input_file(self.rtm_vars)
        self.log("Running...")
        t0 = time.time()
        self.run_rtm()
        tf = time.time()
        self.log("Done in %#.3gs." % (tf-t0))
        result = self.read_output()
        self.clean_up()
        return result
    
    def _write_input_file(self, rtm_vars):
        
        try:
            infile = open(os.path.join(self.working_dir, self.input_file), 'w')
        except:
            raise self.FileSystemError("Couldn't open input file for writing")
        infile.write(str(rtm_vars))
        infile.close()
    
    @property
    @abc.abstractmethod
    def rtm_vars(self): pass
    
    @abc.abstractmethod
    def run_rtm(self): return
    
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
    
    @abc.abstractmethod
    def read_output(self): pass
    
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
    output_file = 'smarts295.ext.txt'
    output_extra = ['log.txt', 'smarts295.out.txt']
    
    @property
    def rtm_vars(self):
        return utils.smarts_cards(settings.translate_smarts(self.config))
    
    def run_rtm(self):
        exe = './%s > log.txt' % self.executable
        self.log("exec command: %s" % exe)
        p = subprocess.Popen(exe, shell=True, cwd=self.working_dir)
        p.wait()
        return
        
    def read_output(self):
        
        """
        try:
            raw_output = open(os.path.join(self.working_dir, self.output_file))
        except IOError:
            raise self.FileSystemError("Can't open the raw output file.")
        """
        output = os.path.join(self.working_dir, self.output_file)
        return numpy.genfromtxt(output, skip_header=1)


class SBdart(_RTM):
    name = 'SBdart'
    bin_path = os.path.join('bin', 'sbdart')
    executable = 'drtx'
    input_file = 'INPUT'
    output_file = 'OUTPUT'
    
    @property
    def rtm_vars(self):
        return utils.Namelist('INPUT', settings.translate_sbdart(self.config))
        
    def run_rtm(self):
        exe = './%s > %s' % (self.executable, self.output_file)
        self.log("exec command: %s" % exe)
        p = subprocess.Popen(exe, shell=True, cwd=self.working_dir)
        p.wait()
        return
    
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
        """
        try:
            raw_output = open(os.path.join(self.working_dir, self.output_file))
        except IOError:
            raise self.FileSystemError("Can't open the raw output file.")
        
        for i in range(3):
            # skip the first couple garbage lines in the output
            next(raw_output)
            
        output = csv.reader(raw_output, delimiter=' ')
        return [float(entry[6]) for entry in output]    #FIXME not really the right data...
        """
        output = os.path.join(self.working_dir, self.output_file)
        return numpy.genfromtxt(output, skip_header=3)


def All(*args, **kwargs):
    """
    Return an EachList containing all the RTM wrappers.
    
    Check out utils.EachList and the corresponding unit tests for more on how
    EachLists work.
    
    You can use this just like you'd use the RTM classes; everything will be
    the same except that all the results will be elements of an EachList.
    """
    return utils.EachList([SMARTS, SBdart])(*args, **kwargs)





