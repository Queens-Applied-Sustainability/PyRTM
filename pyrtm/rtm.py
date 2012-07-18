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
import sys
import re
import shutil
import subprocess
import tempfile
import threading
import time

import settings
import utils
import pysmarts
import pysbdart

_mod_dir = os.path.abspath(os.path.dirname(__file__))

class _RTM(dict):
    """
    Abstract class describing interactions with RTM applications.
    """
    __metaclass__ = abc.ABCMeta
    
    name = None         # How shall I identify myself?
    rtm = None 
    resources = []      # What other important items do I need?
    resource_path = []
    input_file = None   # What is the name of the file I read for input?
    input_translator = None # Who can I call to get the config in my language?
    input_generator = None  # Who can format the config into something I read?
    output_file = None  # To where shall/do I write my output?
    output_extra = []   # What other extra files do I write?
    output_headers = None   # How many garbage lines to I produce?
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
        if self.resources:
            self.log("Linking", no_break=True)
            for resource in self.resources:
                try:
                    self.log("%s" % resource, plain=True, no_break=True)
                    os.symlink(os.path.join(_mod_dir, self.resource_path, resource),
                               os.path.join(self.working_dir, resource))
                except OSError:
                    raise self.FileSystemError("Huh. Can't make some symlinks "\
                        "that I need in order to work. Maybe in a future version "\
                        "I'll be SMARTS enough to fall back to something...")
            self.log(plain=True) # clear the line \n
    
    def get(self, newconfig = {}, raw=False):
        self.update(newconfig)
        self.setup_working_dir()
        cwd = os.getcwd()
        os.chdir(self.working_dir)
        self._write_input_file()
        self._t0 = time.time()
        self.rtm()
        self.t = time.time() - self._t0
        self.log("Done in %#.3gs." % self.t)
        self.read_output()
        os.chdir(cwd)
        self.clean_up()
        if raw:
            return self.result
        return self.standardized()
    
    def read_output(self):
        output_path = os.path.join(self.working_dir, self.output_file)
        try:
            self.result = numpy.genfromtxt(
                            output_path, skip_header=self.output_headers)
        except StopIteration:
            raise self.FileSystemError("Something went wrong reading output!")
    
    def clean_up(self):
        if self.clean_after:
            try:
                shutil.rmtree(self.working_dir)
            except NameError:
                self.log("Nothing to clean -- was it ever created?")
            except OSError:
                self.log("Can't remove the directory. Does it exist?"      
                                                    " Do you have permission?")
            else:
                self.log("Successfully cleaned up temporary files.")
    
    def standardized(self):
        raise NotImplementedError("Subclass and implement me!");
    
    class FileSystemError(Exception): pass


class SMARTS(_RTM):
    name = 'SMARTS'
    resources = ['Albedo', 'CIE_data', 'Gases', 'Solar']
    resource_path = os.path.join('data', 'smarts')
    input_file = 'smarts295.inp.txt'
    config_translator = settings.translate_smarts
    input_generator = utils.smarts_cards
    output_file = 'smarts295.ext.txt'
    output_headers = 1
    output_extra = ['log.txt', 'smarts295.out.txt']
    
    def rtm(self):
        """
        SBdart writes its output to the C standard input, so we need to
        set ourselves up to capture that.
        """
        STANDARD_OUT = 1
        outfile = os.open("blah", os.O_RDWR|os.O_CREAT)
        stdout = os.dup(STANDARD_OUT)
        os.dup2(outfile, STANDARD_OUT)
        pysmarts.smarts()
        os.dup2(stdout, STANDARD_OUT)
        os.close(outfile)
    
    def standardized(self):
        return numpy.array([self.result[:, 0]/1000, self.result[:, 1]*1000])


class SBdart(_RTM):
    name = 'SBdart'
    input_file = 'INPUT'
    config_translator = settings.translate_sbdart
    input_generator = utils.Namelist('INPUT')
    output_file = 'OUTPUT.dat'
    output_headers = 3
    
    def rtm(self):
        """
        SBdart writes its output to the C standard input, so we need to
        set ourselves up to capture that.
        """
        STANDARD_OUT = 1
        outfile = os.open(self.output_file, os.O_RDWR|os.O_CREAT)
        stdout = os.dup(STANDARD_OUT)
        os.dup2(outfile, STANDARD_OUT)
        pysbdart.go()
        os.dup2(stdout, STANDARD_OUT)
        os.close(outfile)
    
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
        
    def standardized(self):
        return numpy.array([self.result[:, 0], self.result[:, 5]])


def All(*args, **kwargs):
    """
    Return an EachList containing all the RTM wrappers.
    
    Check out utils.EachList and the corresponding unit tests for more on how
    EachLists work.
    
    You can use this just like you'd use the RTM classes; everything will be
    the same except that all the results will be elements of an EachList.
    """
    return utils.EachList([SMARTS, SBdart])(*args, **kwargs)





