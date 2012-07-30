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

import os
import shutil
import subprocess
import tempfile

class RTMError(Exception): pass

class Working():
    """Make a unique temporary working directory in which to run the RTM"""
    def __init__(self, cleanup=True):
        """Create our temporary directory and cd into it"""
        self.dir = tempfile.mkdtemp(suffix='_RTM')
        self.cleanup = cleanup
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        """Go back to where we're running, and destroy the temporary dir"""
        if self.cleanup:
            shutil.rmtree(self.dir)
    
    def __str__(self):
        return "<Working: %s>" % self.dir
    
    def link(self, resources, path=""):
        """Caution! resources will be iterated; don't give a string!"""
        [os.symlink(
            os.path.join(path, resource),
            os.path.join(self.dir, resource)
            ) for resource in resources]
    
    def write(self, file_name, content):
        open(os.path.join(self.dir, file_name), 'w').write(content)
    
    def run(self, cmd, logerr=True, errfile="errlog.txt"):
        cmd += " 2> %s" % errfile if logerr else ""
        p = subprocess.Popen(cmd, cwd=self.dir, shell=True)
        p.wait()
        err = open(os.path.join(self.dir, errfile)).read() if logerr else None
        return p.returncode, err
    
    def get(self, file_name, mode='r'):
        """all these files should be closed before finishing with Working"""
        return open(os.path.join(self.dir, file_name), mode)


