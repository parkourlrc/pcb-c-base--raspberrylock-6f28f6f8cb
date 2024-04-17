# -*- coding: utf-8 -*-

import unittest

from raspberrylock import *


class SchlossTest(unittest.TestCase):
    

    def test_decrease_timeouts(self):
        timeouts_expected = {'1': 0}
        timeouts_input = {'1': 1}
        result = decrease_timeouts(timeouts_input)
        self.assertEquals(timeout_expected, result)
        result = decrease_timeouts(result)
        self.assertEquals(timeout_expected, result)

