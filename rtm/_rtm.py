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
import re
import inspect
import shutil
import subprocess
import tempfile
import superhash
import cPickle as pickle
from superhash import superhash


MAX_FILE_CHARS = 42
CACHE_DIR = 'cached'
PRIMARY = ['description', 'longitude', 'latitude']
SECONDARY = ['year', 'month']


class RTMError(Exception): pass


def _vars_to_file(vars):
    """Return a safe string to be used as a file or directory name"""
    clean_vars = [re.sub('[^a-zA-Z0-9_:]', '.', str(v)) for v in vars]
    clean_string = '-'.join(clean_vars)
    if clean_string.startswith('.'):
        clean_string = 'c' + clean_string
    if len(clean_string) > MAX_FILE_CHARS:
        # name was too long; use hash instead hash instead.
        return str(clean_string.__hash__())
    return clean_string


class Working(object):
    """Get previously computed result or run rtm"""
    def __init__(self, target, config):
        
        primary = _vars_to_file(config[v] for v in PRIMARY)
        secondary = _vars_to_file(
            getattr(config['time'], v) for v in SECONDARY)
        rundir = _vars_to_file([superhash(config)])

        path = os.path.join(target, primary, secondary, rundir)

        try:
            os.makedirs(path)
            self.cached = False
        except OSError as err:
            if err.errno is 17:
                # we've already run and (hopefully) cached this
                self.cached = True
            else:
                raise # some other OSError came up

        self.config = config
        self.dir = path
        self.runpickle = 'run.pickle'
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        """asdf"""
        pass
    
    def __str__(self):
        return "<Working: %s>" % self.dir
    
    def link(self, resources, path=""):
        """link some stuff in"""
        if type(resources) == str:
            resources = [resources]
        [os.symlink(
            os.path.join(path, resource),
            os.path.join(self.dir, resource)
            ) for resource in resources]
    
    def write(self, file_name, content):
        open(os.path.join(self.dir, file_name), 'w').write(content)
    
    def run(self, cmd, errfile="errorlog.txt"):
        pkl = os.path.join(self.dir, self.runpickle)

        try:
            out = pickle.load(open(pkl, 'rb'))

        except IOError:            
            cmd += " 2> %s" % errfile
            p = subprocess.Popen(cmd, cwd=self.dir, shell=True)
            p.wait()
            err = open(os.path.join(self.dir, errfile)).read()
            out = [p.returncode, err, self.config]

            cachefile = open(pkl, 'wb')
            pickle.dump(out, cachefile)
            cachefile.close()

        return out
    
    def get(self, file_name, mode='r'):
        """all these files should be closed before finishing with Working"""
        return open(os.path.join(self.dir, file_name), mode)


def config_cache(func):
    cache = {}
    @wraps(func)
    def wrapcache(*args, **kwargs):
        try:
            val = cache[config._cache_key]
            print 'hit'
        except KeyError:
            print 'miss'
            val = func(*args, **kwargs)
            cache.update({config._cache_key: val})
        return val
    return wrapcache


class CacheDict(dict):
    """cache calculated stuff"""

    def __init__(self, *args, **kwargs):
        self._cache = {}
        self._cache_key = None
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        self._cache_key = str(self.__hash__())
        super(CacheDict, self).__setitem__(key, value)

    _ignore = [name for name, thing in inspect.getmembers(dict)]

    def __getattribute__(self, attr, *args, **kwargs):
        if (not attr.startswith('_') and not attr in self._ignore):
            try:
                val = self._cache[self._cache_key][attr]
                print 'hit'
            except KeyError:
                val = dict.__getattribute__(self, attr)
                try:
                    self._cache[self._cache_key].update({attr: val})
                except KeyError:
                    self._cache[self._cache_key] = {}
                print 'miss'
        else:
            val = dict.__getattribute__(self, attr)
        return val

    def __hash__(self):
        try:
            return reduce(lambda x,y:x^y, map(hash, self.items()))
        except TypeError:
            return hash(str(self))

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("expected 1 argument, got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]


class CallableDict(dict):
    """A lazy dictionary who will call its keys on access"""

    def __init__(self, *args, **kwargs):
        self._cache = {}
        super(CallableDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if not hasattr(value, '__call__'):
            raise TypeError('value ' + str(value) + ' must be callable')
        super(CallableDict, self).__setitem__(key, value)

    def __getitem__(self, key):
        try:
            val = self._cache[key]
            print 'cache hit'
        except KeyError:
            print 'cache miss'
            val = super(CallableDict, self).__getitem__(key)()
            self._cache[key] = val
        return val

    def __delitem__(self, key):
        super(CallableDict, self).__delitem__(key)
        if key in self._cache:
            del self._cache[key]

    def update(self, d):
        for k, v in d.items():
            self.__setitem__(k, v)

