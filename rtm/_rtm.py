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
import shutil
import subprocess
import tempfile
import superhash
import cPickle as pickle
from superhash import superhash
import settings


class RTMError(Exception): pass


MAX_FILE_CHARS = 42
CACHE_DIR = 'cached'
PRIMARY = ['description', 'longitude', 'latitude']
SECONDARY = ['year', 'month', 'day']

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path):
    return os.path.join(_ROOT, 'data', path)


def _vars_to_file(vars):
    """Return a safe string to be used as a file or directory name"""
    clean_vars = [re.sub('[^a-zA-Z0-9_:\-]', '.', str(v)) for v in vars]
    clean_string = '-'.join(clean_vars)
    if clean_string.startswith('.'):
        clean_string = 'c' + clean_string
    if len(clean_string) > MAX_FILE_CHARS:
        # name was too long; use hash instead hash instead.
        return str(clean_string.__hash__())
    return clean_string


class Model(dict):
    """The parent of what you probably need to use"""

    def __init__(self, userconfig=None, target='.', cleanup=True,
                                                            *args, **kwargs):
        required = ['description', 'latitude', 'longitude', 'time']
        config = dict(
            {k: v for k, v in settings.defaults.items() if k in required})
        config.update(userconfig or {})
        self.target = target
        self.cleanup = cleanup
        super(Model, self).__init__(config, *args, **kwargs)

    def __hash__(self):
        return hash(dict.__str__(self) + str(self.__class__))


class Working(object):
    """work with the executables"""
    def __init__(self, model):
        
        # set up the directory variables
        primary = _vars_to_file(model[v] for v in PRIMARY)
        secondary = _vars_to_file(
            getattr(model['time'], v) for v in SECONDARY)
        rundir = _vars_to_file([str(hash(model))])

        path = os.path.join(model.target, primary, secondary, rundir)

        try:
            state = model._working_state[hash(model)]
        except AttributeError:
            model._workings_state = {}
        except KeyError:
            pass
        finally:
            state = {'dir_created': False}

        if not state['dir_created']:
            try:
                os.makedirs(path)
            except OSError as err:
                if err.errno is not 17:
                    raise

            state['dir_created'] = True

        self.model = model
        self.path = path
        self.state = state
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        """save state back to model"""
        try:
            self.model._workings_state[hash(self.model)].update(self.state)
        except KeyError:
            self.model._workings_state[hash(self.model)] = self.state
    
    def __str__(self):
        return "<Working: %s>" % self.path
    
    def link(self, resources, path=""):
        """link some stuff in"""
        if type(resources) == str:
            resources = [resources]
        try:
            [os.symlink(
                os.path.join(path, resource),
                os.path.join(self.path, resource)
                ) for resource in resources]
        except OSError as err:
            if err.errno is not 17:
                raise
    
    def write(self, file_name, content):
        if file_name in self.state.get('writes', []):
            return
        else:
            open(os.path.join(self.path, file_name), 'w').write(content)

        if not self.state.get('writes'):
            self.state['writes'] = [file_name]
        else:
            self.state['writes'].append(file_name)

    
    def run(self, cmd, outfile, errfile=None):

        try:
            # first try to get the local cache
            run_out = self.state['outfile'][cmd]
        except KeyError:
            self.state['outfile'] = {}

        # no local cache, check for a pickle
        safe_cmd = _vars_to_file([cmd])
        errfile = errfile or 'err-%s' % outfile
        picklename = 'run %s.pickle' % safe_cmd
        picklepath = os.path.join(self.path, picklename)

        try:
            run_out = pickle.load(open(picklepath, 'rb'))
            self.state['outfile'][cmd] = run_out
            return run_out
        except IOError:
            pass
       
        # no pickle, so now actually run the command
        cmd += ' 2> %s' % errfile
        p = subprocess.Popen(cmd, cwd=self.path, shell=True)
        p.wait()
        err = open(os.path.join(self.path, errfile)).read()
        run_out = [p.returncode, err, self.model]
        self.state['outfile'][cmd] = run_out

        with open(picklepath, 'wb') as cache_pickle:
            pickle.dump(run_out, cache_pickle)

        return run_out
    
    def get(self, file_name, mode='r'):
        """all these files should be closed before finishing with Working"""
        return open(os.path.join(self.path, file_name), mode)


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
        except KeyError:
            val = dict.__getitem__(self, key)()
            self._cache[key] = val
        return val

    def __delitem__(self, key):
        super(CallableDict, self).__delitem__(key)
        if key in self._cache:
            del self._cache[key]

    def update(self, d):
        for k, v in d.items():
            self.__setitem__(k, v)

