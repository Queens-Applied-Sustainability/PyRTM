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

# import unittest
# from datetime import datetime
# from .. import sbdart

# class TestNamelist(unittest.TestCase):

# 	def assertNamelist(self, config, namelist):
# 		namelistified = sbdart.namelistify(sbdart.translate(config))
# 		self.assertEqual(namelistified, namelist)

# 	def testDefault(self):
# 		nl = '&INPUT\n TCLOUD = 0\n IOUT = 1\n ZOUT = 0, 50\n '\
# 			'IDATM = 4\n IDAY = 101\n UW = 0.967465405088\n '\
# 			'WLINF = 0.28\n ALON = 283.7\n WLSUP = 2.5\n '\
# 			'WLINC = 0.01\n TIME = 17.0\n TBAER = 0.08\n ISALB = 6\n '\
# 			'PBAR = 1013.25\n ALAT = 44\n IAER = 1\n XCO2 = 390\n '\
# 			'ZCLOUD = 6\n /\n'
# 		self.assertNamelist({}, nl)

# 	def testExample1(self):
# 		# IDATM is hard-coded as 4
# 		# ISAT is defaulted as 0
# 		config = {
# 			'lower_limit': 0.25,
# 			'upper_limit': 1.0,
# 			'resolution': 0.005,
# 			}
# 		nl = '&INPUT\n TCLOUD = 0\n IOUT = 1\n ZOUT = 0, 50\n '\
# 			'IDATM = 4\n IDAY = 101\n UW = 0.967465405088\n '\
# 			'WLINF = 0.25\n ALON = 283.7\n WLSUP = 1.0\n '\
# 			'WLINC = 0.005\n TIME = 17.0\n TBAER = 0.08\n ISALB = 6\n '\
# 			'PBAR = 1013.25\n ALAT = 44\n IAER = 1\n XCO2 = 390\n '\
# 			'ZCLOUD = 6\n /\n'
# 		self.assertNamelist(config, nl)






# if __name__ == '__main__':
# 	unittest.main()

