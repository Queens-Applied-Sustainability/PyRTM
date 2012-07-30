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
from setuptools import setup
from setuptools.command.install import install as DistutilsInstall

class CompileAndInstall(DistutilsInstall):
    def comp(self, which):
        import subprocess
        makers = ['make', 'gmake']
        fcompilers = ['f90', 'ifort', 'pgfortran', 'f95', 'gfortran']
        for mk in makers:
            for fc in fcompilers:
                fbuild = subprocess.Popen('%s FC=%s' % (mk, fc),
                                          cwd=os.path.join('bin', which),
                                          shell=True)
                fbuild.wait()
                print "RETURN CODE FOR %s %s: %d" % (mk, fc, fbuild.returncode)
                if fbuild.returncode == 0:
                    return # Great!
                if fc is fcompilers[-1] and mk is makers[-1]:
                    print "FAIL: Couldn't build fortran sources."
                    import sys
                    sys.exit(1)
        
    def run(self):
        self.comp('sbdart')
        self.comp('smarts')
        DistutilsInstall.run(self)


setup(
    name='RTM',
    version='0.0.7',
    author='Philip Schleihauf',
    author_email='uniphil@gmail.com',
    license='license.txt', #????
    description='Numerical Computations for Radiative Transfer Modelling',
    long_description=open('README.txt').read(),
    #url='https://github.com/uniphil/FMM',
    packages=['rtm'],
    scripts=[
        'bin/sbdart/sbdart',
        'bin/smarts/smarts295',
        ],
    install_requires=['numpy'],
    cmdclass={'install': CompileAndInstall},
    )
    
    
