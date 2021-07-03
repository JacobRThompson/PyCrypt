import unittest
import time
import numpy as np
import json
from PyArray import core, utils

# ------------------------------------------------------------------------------
# Global definitions and setup

doLog_global = True

with open('sample.txt') as infile:
    str_sampleText = infile.readline()
    arr_sampleText = core.Encode(str_sampleText)

    if doLog_global:
        print(f"str_sampleText size:\t{len(str_sampleText)}")


def Run(*tests: str):
    pass


class LogTest(unittest.TestCase):
    """ TestCase that automatically logs execution times of tests"""

    def __init__(self,  *args, doLog=True, **kwargs) -> None:

        # flag to use logging (suppressed if doLog_global == False)
        self._doLog = doLog
        super().__init__(*args, **kwargs)

    @property
    def doLog(self):
        return self._doLog if doLog_global else False

    @doLog.setter
    def doLog(self, x):
        self._doLog = x

    def setUp(self):
        """Used to diplay name of current test"""
        if self.doLog:
            self.startTime = time.time()
            print(f"{self.id}:\t", end="")

    def tearDown(self):
        """Used to display time elapsed for each test"""
        if self.doLog:
            t = time.time()-self.startTime
            print(f"t:\t{t}")

# ------------------------------------------------------------------------------
# Unit Test Definitions


class UnitUtils(LogTest):

    def test_loadPresets(self):

        # load 2 dummy entries.
        dict_cipher, dict_map = core.LoadPreset("__TEST__", "__TEST__")
        self.assertDictEqual(dict_cipher, {"name": "__TEST__",
            "noKeywords": "NA", "formula": "NA", "inverse": "NA"})

        self.assertDictEqual(dict_map, {"name": "__TEST__"})

        # Try to load single entry that is not in presets
        dict_failure = core.LoadPreset(maps="!!??!!")
        self.assertEqual(dict_failure, None)

    def test_loadPresets(self):

        # load 2 dummy entries.
        dict_cipher, dict_map = core.LoadPreset("__TEST__", "__TEST__")
        self.assertDictEqual(dict_cipher, {"name": "__TEST__",
            "noKeywords": "NA", "formula": "NA", "inverse": "NA"})

        self.assertDictEqual(dict_map, {"name": "__TEST__"})

        # Try to load single entry that is not in presets
        dict_failure = core.LoadPreset(maps="!!??!!")
        self.assertEqual(dict_failure, None)


class UnitEncrypt(LogTest):
    def test_encodeAndDecode_noMap(self):

        arr_encoded = core.Encode(str_sampleText)
        str_decoded = core.Decode(arr_encoded)
        self.assertEqual(str_sampleText, str_decoded)

    def test_EncodeAndDecode_withMap(self):
        """Tests Encode() and Decode() for an inverting map"""

    def test_VigenereA(self):
        pass


# suite = unittest.TestLoader().loadTestsFromTestCase(unCore)
# unittest.TextTestRunner(verbosity=0).run(suite)