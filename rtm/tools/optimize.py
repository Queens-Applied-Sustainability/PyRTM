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

>>> from rtm import SMARTS
>>> from rtm.tools import Optimizer
>>> model = SMARTS({'description': 'optimizer test'})
>>> optimizer = Optimizer('aerosol_optical_depth', (0, 0.4), 0.001)
>>> optimizer.optimize(model, target_irradiance=836.0)
0.092556335617052121
"""

from fmm import zeroin, BadBoundsError, NoConvergeError


class Optimizer(object):
    """
    Optimize a model for a target irradiance.

    Possible future extension: plug in a custom solver?
    """
    
    def __init__(self, parameter, bounds, tolerance,
        irradiance='global'):
        """
        parameter: a model config setting that the particular rtm supports.
        bounds: a two-elemnt tuple defining some x which bound the solution.
        a solution returned will be within +/- tolerance + epsilon of whatever
        target irradiance is passed to optimize.
        """
        self.parameter = parameter
        self.bounds = bounds
        self.tolerance = tolerance
        self.irradiance = irradiance

    def optimize(self, model, target_irradiance):
        self.meta = {
            'model': dict(model),
            'parameter': self.parameter,
            'target_irradiance': target_irradiance,
            'iterations': {},
            }

        def f(x):
            model.update({self.parameter: x})
            diff = model.irradiance[self.irradiance] - target_irradiance
            self.meta['iterations'].update({x: diff})
            return diff

        result = zeroin(self.bounds[0], self.bounds[1], f, self.tolerance)
        self.meta['model'].update({self.parameter: result})

        return result

    def clean_up(self):
        raise NotImplementedError
