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



import sys
import unittest
from .. import utils

class testNamelist(unittest.TestCase):
        
    def testBlockName(self):
        "Block name is not hard-coded"
        fnl = utils.Namelist("BLOCK")
        self.assertEqual(str(fnl), '$BLOCK\n$END')
        
    def testBadBlockName(self):
        "Block name must conform to valid fortran variable specs"
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, "_")
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, " ")
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, ".")
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, "0")
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, "0A")
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, 0)
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, [])
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, {})
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, ())
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, "")
        self.assertRaises(utils.Namelist.VarError, utils.Namelist, None)
    
    def testEmpty(self):
        "Boundary condition: empty namelist"
        fnl = utils.Namelist("INPUT")
        self.assertEqual(str(fnl), '$INPUT\n$END')
    
    def testEmptyVal(self):
        "Namelist values can't be None or empty iterables"
        fnl = utils.Namelist("INPUT")
        self.assertRaises(utils.Namelist.NoValueError, fnl.update, {"N": []})
        self.assertRaises(utils.Namelist.NoValueError, fnl.update, {"N": {}})
        self.assertRaises(utils.Namelist.NoValueError, fnl.update, {"N": ()})
        self.assertRaises(utils.Namelist.NoValueError, fnl.update, {"N": None})
    
    def testEmptyString(self):
        "Empty strings are allowed"
        fnl = utils.Namelist("INPUT", {"ESTRING": ""})
        self.assertEqual(str(fnl), '$INPUT\n ESTRING = \'\'\n$END')
    
    def testInt(self):
        "Integer values are allowed"
        fnl = utils.Namelist("INPUT", {"INT": 1})
        self.assertEqual(str(fnl), '$INPUT\n INT = 1\n$END')
        
    def testFloat(self):
        "Floating point values are allowed"
        fnl = utils.Namelist("INPUT", {"FLOAT": 1.1})
        self.assertEqual(str(fnl), '$INPUT\n FLOAT = 1.1\n$END')
        
    def testString(self):
        "String values are allowed"
        fnl = utils.Namelist("INPUT", {"STRING": "Hello"})
        self.assertEqual(str(fnl), '$INPUT\n STRING = \'Hello\'\n$END')
    
    def testList(self):
        "Lists are allowed"
        fnl = utils.Namelist("INPUT", {"LIST": [0, 1]})
        self.assertEqual(str(fnl), '$INPUT\n LIST = 0, 1\n$END')
    
    def testTupple(self):
        "Tupples are allowed (output identical to lists)"
        fnl = utils.Namelist("INPUT", {"TUP": (0, 1)})
        self.assertEqual(str(fnl), '$INPUT\n TUP = 0, 1\n$END')
    
    def testBadKey(self):
        "Fortran variables must be alpha-numeric and must begin with a letter"
        fnl = utils.Namelist("INPUT")
        self.assertRaises(utils.Namelist.VarError, fnl.update, {"_": 0})
        self.assertRaises(utils.Namelist.VarError, fnl.update, {" ": 0})
        self.assertRaises(utils.Namelist.VarError, fnl.update, {".": 0})
        self.assertRaises(utils.Namelist.VarError, fnl.update, {"0": 0})
        self.assertRaises(utils.Namelist.VarError, fnl.update, {"0A": 0})
        self.assertRaises(utils.Namelist.VarError, fnl.update, {0: 0})
        self.assertRaises(utils.Namelist.VarError, fnl.update, {"": 0})
    
    def testGoodNumKey(self):
        "Fortran variables may contain numbers"
        fnl = utils.Namelist("INPUT", {"Z0": 0})
        self.assertEqual(str(fnl), '$INPUT\n Z0 = 0\n$END')
    
    def testMultiEntries(self):
        "Namelist entries should be separated a comma-newline"
        fnl = utils.Namelist("INPUT", {"ZERO": 0, "ONE": 1})
        self.assertEqual(str(fnl), '$INPUT\n ZERO = 0,\n ONE = 1\n$END')

    def test2dArray(self):
        "Lists containing non-string itterables are not allowed"
        fnl = utils.Namelist("INPUT")
        self.assertRaises(utils.Namelist.ArrayError,
                                                fnl.update, {"L2":[[0],1]})
        self.assertRaises(utils.Namelist.ArrayError,
                                                fnl.update, {"L2":[(0,),1]})
        self.assertRaises(utils.Namelist.ArrayError,
                                                fnl.update, {"L2":[{0:1},2]})
        
    def testArrayOfStrings(self):
        "Lists containing string iterables are allowed"
        fnl = utils.Namelist("INPUT", {"STRINGS": ["one", "two"]})
        self.assertEqual(str(fnl), '$INPUT\n STRINGS = \'one\', \'two\'\n$END')
        
    
class testUnderline(unittest.TestCase):
    
    def testIndent(self):
        "Underline should align with input character"
        self.assertEqual(utils.underline('a'), '\n a'
                                               '\n -')
    
    def testStrong(self):
        "Use a double-underline for strong statements"
        self.assertEqual(utils.underline('a', True), '\n a'
                                                     '\n =')
    
    def testTypes(self):
        "Any stringable type should work"
        self.assertEqual(utils.underline(0), '\n 0\n -')
        self.assertEqual(utils.underline(0.0), '\n 0.0\n ---')
        self.assertEqual(utils.underline([]), '\n []\n --')
        self.assertEqual(utils.underline(object), "\n <type 'object'>"
                                                  '\n ---------------')
        self.assertEqual(utils.underline('hello world'), '\n hello world'
                                                         '\n -----------')


class testPrintBrander(unittest.TestCase):
    
    class PrintIntercept(object):
        def __init__(self):
            self.clear()
        def write(self, msg):
            self.cache += str(msg)
        def clear(self):
            self.cache = ""
    
    def setUp(self):
        self.stdout = sys.stdout
        self.printed = self.PrintIntercept()
        sys.stdout = self.printed
    
    def testEmptyBrands(self):
        "Empty/none values for brand should just print normally"
        self.printed.clear()
        pb = utils.print_brander("")
        pb("hello")
        self.assertEqual(self.printed.cache, "hello\n")
        self.printed.clear()
        pb = utils.print_brander(None)
        pb("hello")
        self.assertEqual(self.printed.cache, "hello\n")
        self.printed.clear()
        pb = utils.print_brander([])
        pb("hello")
        self.assertEqual(self.printed.cache, "hello\n")
    
    def testZeroBrand(self):
        "A zero as the brand should still print even though bool(0) is False"
        self.printed.clear()
        pb = utils.print_brander(0)
        pb("hello")
        self.assertEqual(self.printed.cache, "0: hello\n")
    
    def testBrand(self):
        "Branding should work"
        self.printed.clear()
        pb = utils.print_brander("brand")
        pb("hello")
        self.assertEqual(self.printed.cache, "brand: hello\n")
    
    def tearDown(self):
        sys.stdout = self.stdout


class TestInstantiator(unittest.TestCase):
    
    def testInstance(self):
        "Instantiator should return an instance, not a class"
        @utils.instantiator
        class o(object):
            pass
        self.assertTrue(isinstance(o, object))


class TestPopenAndCall(unittest.TestCase):
    "I actually don't know how to test this. Hmm..."
    pass


class TestEachList(unittest.TestCase):
    
    class SomeClass(object):
        def __init__(self, someinitarg="some default"):
            self.someattr = someinitarg
        def some_method(self, somearg=""):
            return "something %s" % somearg
        def __eq__(self, other):
            return self.someattr == other.someattr
    
    def testEmptyInit(self):
        "Initialization of an empty list"
        el = utils.EachList([])
        self.assertListEqual(el, [])
        
    def testInit(self):
        "Initialization of an normal list"
        el = utils.EachList([0])
        self.assertListEqual(el, [0])

    def testObjInit(self):
        "Initialization of a list of objects"
        el = utils.EachList([self.SomeClass])()
        self.assertListEqual(el, [self.SomeClass()])
        el = utils.EachList([self.SomeClass])(1)
        self.assertListEqual(el, [self.SomeClass(1)])
    
    def testAttributeAccess(self):
        "Access of normal objects' attributes"
        el = utils.EachList([self.SomeClass])(1)
        self.assertListEqual(el.someattr, [1])
    
    def testAttributeSet(self):
        "Set attributes on each object"
        el = utils.EachList([self.SomeClass])()
        el.new_attr = 1
        self.assertListEqual(el.new_attr, [1])
    
    def testAttributeDeletion(self):
        "Delete objects' attributes"
        el = utils.EachList([self.SomeClass])()
        el.new_attr = 1
        del el.new_attr
        self.assertRaises(AttributeError, getattr, el, 'new_attr')
    
    def testMethodCall(self):
        "Call methods of objects"
        el = utils.EachList([self.SomeClass])()
        self.assertListEqual(el.some_method(), ["something "])
        self.assertListEqual(el.some_method("more"), ["something more"])
    
    def testElementIndexAccess(self):
        "The list still works like a list"
        el = utils.EachList([9,8,7])
        self.assertEqual(el[0], 9)
        self.assertEqual(el[1], 8)
        self.assertEqual(el[-1], 7)
    
    def testListSlicing(self):
        "The list can still be sliced and diced"
        el = utils.EachList([9,8,7])
        self.assertListEqual(el[1:], [8,7])
        self.assertListEqual(el[:1], [9])
        self.assertListEqual(el[-1:], [7])
        self.assertListEqual(el[:-1], [9,8])
    
    def testListMethods(self):
        "List methods still work on the EachList itself. Is this expected?!"
        el = utils.EachList([0])
        el.append(1)
        self.assertListEqual(el, [0, 1])
        self.assertEqual(el.pop(), 1)


if __name__ == '__main__':
    unittest.main()

