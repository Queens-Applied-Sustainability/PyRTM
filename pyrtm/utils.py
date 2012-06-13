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

import re
import threading
import subprocess
from collections import Iterable

class Namelist(dict):
    """Dict that returns a formatted Fortran Namelist when stringified.
    
    Integers, floats, strings, and 1-dimensional arrays (lists or tupples, or
    any non-string Iterable) should work as expected.
    
    Only one NAMELIST block is supported, which makes sense in this
    implementation since we're subclassing dict and using the dict's keys/values
    to write the namelist. The block name must be passed to the constructor.
    
    Use instances of this class like any other dict to hold stuff, and then just
    cast the object to a string to get the Fortran NAMELIST version out.
    
    This code works with a Fortran script that I compiled with gfortran. I
    could not find the actual fortran specifications for NAMELIST formatting
    anywhere, so your mileage may varry. If you know of these specs, please
    contact me -- uniphil@gmail.com.
    """
    
    def __init__(self, block, *args, **kwargs):
        super(Namelist, self).__init__(*args, **kwargs)
        self._check_fortran_var_name(block)
        self.header = block
    
    def __repr__(self):
        out = '$%s\n' % self.header
        fvals = (" %s = %s" %
                    (key, self.fval(val)) for key, val in self.items())
        out += ',\n'.join(fvals)
        out += '%s$END' % ('\n' if bool(self.items()) else '')
        return out
    
    def fval(self, val, first_level=True):
        """
        Return a variable stringified in a fortran-readable mannor
        """
        if isinstance(val, str): # strings are treated 'specially'.
            return "'%s'" % val
        elif isinstance(val, Iterable):
            return ", ".join(self.fval(v, False) for v in val)
        else:
            return str(val)
    
    def update(self, newstuff):
        "Validate the values going in"
        for key, val in newstuff.items():
            if (not bool(val)) and (not val==0) and (not isinstance(val, str)):
                raise self.NoValueError("No empty values allowed.")
            if isinstance(val, Iterable) and not isinstance(val, str):
                raise self.ArrayError("Only 1-dimensional arrays allowed.")
            self._check_fortran_var_name(key)
        super(Namelist, self).update(newstuff)
    
    def _check_fortran_var_name(self, key):
        if not isinstance(key, str):
            raise self.VarError("Fortran variable name must be a string.")
        if re.match("^[a-zA-Z][a-zA-Z0-9]+$", key) is None:
            raise self.VarError("Invalid fortran variable name.")
            
    class NoValueError(Exception): pass
    class VarError(Exception): pass
    class ArrayError(Exception): pass


def popenAndCall(onExit, *popenArgs, **popenKWArgs):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that 
    would give to subprocess.Popen.
    """
    def runInThread(onExit, popenArgs, popenKWArgs):
        proc = subprocess.Popen(*popenArgs, **popenKWArgs)
        proc.wait()
        onExit()
        return
    thread = threading.Thread(target=runInThread,
                              args=(onExit, popenArgs, popenKWArgs))
    thread.start()
    return thread # returns immediately after the thread starts


def underline(string, strong=False):
    "Trivial utility to format emphasized output."
    return '\n %s\n %s' % (string, ('=' if strong else '-')*len(str(string)))


def print_brander(brand):
    """
    Simple utility to 'brand' print statments according to who calls them.
    
    The brand is the stringified version of whatever is passed to the closure.
    If nothing or an empyt/None value is passed in, it will not brand the output
    and behave just like a regular print.
    """
    def printer(anything):
        bstring = "%s: " % brand if bool(brand) or brand == 0 else ""
        print("%s%s" % (bstring, anything))
    return printer

def instantiator(cls):
    "Returns an instantiation of the class, intended for use as a decorator"
    return cls()


class EachList(list):
    """
    A list who behaves like her elements.
    
    You can access the list items' attributes by asking for the attribute from
    the list. You can call the list items' methods by calling that method on the
    list itself. You'll always get an eachList back whose elements are the
    result of whatever operation you just performed.
    """
        
    def __getattr__(self, attr):
        return EachList([getattr(thing, attr) for thing in self])
    
    def __setattr__(self, attr, val):
        return EachList([setattr(thing, attr, val) for thing in self])

    def __call__(self, *args, **kwargs):
        return EachList([thing(*args, **kwargs) for thing in self])
    
    def __delattr__(self, attr):
        for thing in self:
            delattr(thing, attr)
    


class RTMConfig(dict):
    # TODO: implement white-list key checking
    # TODO: implement value validation
    pass



