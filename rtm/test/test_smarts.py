# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 17:29:12 2013

@author: rob
"""

import shutil
import unittest
import rtm


class TestSmartsBase(unittest.TestCase):
    def setUp(self):
        test_config = {'description': 'test smarts'}
        self.smarts = rtm.SMARTS(test_config)
        primary = rtm._rtm.PRIMARY
        self.test_dir = rtm._rtm._vars_to_file(
                                    self.smarts[v] for v in primary)
    
    
    def get_cardfile(self):
        card_filename = rtm.smarts.input_file
        return self.working.get(card_filename)


class TestSmarts(TestSmartsBase):
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_standard_atmos(self):
        standard_atmos = {
            'atmosphere': 'sub-arctic summer',
            'smarts_use_standard_atmos': True,
        }
        self.smarts.update(standard_atmos)
        self.working = rtm._rtm.Working(self.smarts)
        print 'IRRADIANCE', self.smarts.irradiance['global'] # force run
        with self.get_cardfile() as card_file:
            cards = card_file.readlines()        
        print ''.join(cards)
        assert cards[3].startswith('1'), 'card three did not start with 1'
        assert cards[4].startswith('\'SAS\''), 'standard atmosphere not selected'

    def test_no_standard_atmos(self):
        standard_atmos = {
            'smarts_use_standard_atmos': False,
        }
        self.smarts.update(standard_atmos)
        self.working = rtm._rtm.Working(self.smarts)
        self.smarts.irradiance['global'] # force smarts to run
        with self.get_cardfile() as card_file:
            cards = card_file.readlines() 
        print ''.join(cards)
        assert cards[3].startswith('0'), 'card three did not start with 0'
