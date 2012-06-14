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
import re
import subprocess
import threading

from collections import Iterable


def smarts_cards(sconf):
    """ BLAH BLAH BLHA """
    
    annoying = {'content': ''}
    def card_print(something, comment=None, no_break=False):
        annoying['content'] += str(something)
        if comment:
            annoying['content'] += ' \t! %s' % comment
        if not no_break:
            annoying['content'] += '\n'
    
    # CARD 1
    card_print(sconf.get('COMNT', 'Hello_world'), '1 COMNT')
    
    # CARD 2
    card_print(1, '2 ISPR mode select')
    card_print('0.0003, 0, 0.1') # FIXME don't hard-code
    
    # CARD 3
    card_print(0, '3 IATMOS mode select')
    card_print('-44, 50, SUMMER, -44') # FIXME don't hard-code some
    
    # Card 4
    card_print(2, '4 IH2O mode select')
    
    # Card 5
    card_print(1, '5 IO3 mode select') # use default ozone FIXME
    
    # Card 6
    card_print(1, '6 IGAS') # use defaults	
    
    # Card 7
    card_print('390, 0, 1', '7 qCO2 ppm') # FIXME
    card_print(0)
    """
    # Card 8
    card_print('USER', '8 AEROS')
    card_print('1, 1, 0.8, 0.7') # FIXME don't hard-code
    
    # Card 9
    card_print(1, '9 ITURB')
    card_print(1) # FIXME Horray iterated value?!
    "" "
    # Card 10
    card_print(5, '10 IALBDX')
    card_print(0)
    
    # Card 11
    card_print('280, 4000, 1, 1367', '11 blergh')
    "" "
    # Card 12
    card_print(2, '12 IPRT')
    card_print('280, 4000, 2')
    card_print('5')
    card_print('2')
    card_print('3')
    card_print('4')
    card_print('5')
    card_print('11')
    
    # Card 13
    card_print(0, '13 ICIRC')
    
    # Card 14
    card_print(0, '14 ISCAN')
    
    # Card 15
    card_print(0, '15 ILLUM')
    
    # Card 16
    card_print(0, '16 IUV')
    
    # Card 17
    card_print(3, '17 IMASS')
    card_print('2012, 6, 14, 12, 44, -73, -5')
    
    """
    return annoying['content']
    
    """
    
    2 -> mode 1 site pressure 
    2a (we input), altitude, height=0
    
    3 -> mode 0
    3a TAIR(const), RH, SEASON(calculate by day), TDAY(calculate)
    
    4 -> mode 2
    
    5 -> mode 1 (will use ussa)
    
    6 -> mode 1 (const for now, could play with proximity to cities)
    
    7 -> 390 (or whatever is current)
    7a-> mode 0 (NEW!!!)
    
    8 -> USER
    8a ALPHA1, ALPHA2, OMEGL, GG (const or switched by rural/urban/marine)
    
    9 -> mode 1
    9a BETA (what we iterate)
    
    10 -> 3-66 choose an albedo based on month
    10b -> 0 ITILT
    
    11 -> WLMN and WLMX 280 - ... (match sbdart), SUNCOR SOLARC -> 1(ignored based on 17), 1367
    
    12 -> 2 IPRT (separate spectral and variable results files)
    12a -> (match spectral range to sbdart/11), match interval to sbdart
    12b -> 16 (number of variables for 12c)
    12c -> 2-5,11,15-20,27-31
    
    13 -> mode 0 ICIRC
    
    14 -> mode 0 ISCAN
    
    15 -> 0 ILLUM
    
    16 -> 0 IUV
    
    17 -> mode 3 IMASS
    17a -> ...
    
    
    
    """
    
    


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
    return '\n %s\n %s' % (string, ('=' if strong else '-') * len(str(string)))


def print_brander(brand):
    """
    Simple utility to 'brand' print statments according to who calls them.
    
    The brand is the stringified version of whatever is passed to the closure.
    If nothing or an empyt/None value is passed in, it will not brand the output
    and behave just like a regular print.
    """
    def printer(anything='', plain=False, no_break=False):
        bstring = "%s: " % brand if bool(brand) or brand == 0 else ""
        branded = anything if plain else "%s%s" % (bstring, anything)
        if not no_break:
            print(branded)
        else:
            print branded,
    return printer

def instantiator(cls):
    """
    Returns an instantiation of the class.
    
    This is intended for use as a decorator.
    The returned object will have the same name as the class it was passed.
    """
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
    
    #def __getitem__(self, each_slice): #FIXME FIXME FIXME
    #    return EachList([list.__getitem__(thing, each_slice) for thing in self])
    


class RTMConfig(dict):
    # TODO: implement white-list key checking
    # TODO: implement value validation
    pass


class _Translation(object):
    "Base class for translations"
    def __call__(self, foreign):
        native = {}
        for key, val in foreign.iteritems():
            native.update(getattr(self, key)(val))
        return native



