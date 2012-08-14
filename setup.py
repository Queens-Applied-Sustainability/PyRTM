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


setup(
    name='RTM',
    version='0.1.1',
    author='Philip Schleihauf',
    author_email='uniphil@gmail.com',
    license='license.txt', #????
    description='Numerical Computations for Radiative Transfer Modelling',
    long_description=open('README.txt').read(),
    #url='https://github.com/uniphil/FMM',
    packages=['rtm'],
    #package_data={'':['*.dat', '*.DAT']},
    include_package_data=True,
    scripts=[
        'bin/sbdart/sbdart',
        'bin/smarts/smarts295',
        ],
    
    #install_requires=['numpy'],
    )
    
    
