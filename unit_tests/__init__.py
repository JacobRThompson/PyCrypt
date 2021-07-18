import unittest
import time
import importlib
import json

from os import path

class LogTest(unittest.TestCase):
    """ TestCase that automatically logs execution times of tests"""

    def __new__(cls, doLog=True) -> None:

        newInstance = super().__new__(cls)

        # flag to use logging (suppressed if doLog_global == False)
        newInstance._doLog = doLog

        return newInstance

    @property
    def doLog(self):
        # NOTE: We always re-lookup config file in case its contents have
        # changed.

        # Get the name of the class invoking this method
        className = self.__class__.__name__

        # Open and then read the unitTests section of config file
        with open(path.join(path.abspath('..'), "config.JSON"), 'r') as config:
            settings = json.load(config)["unitTests"]

            # check if there any flags that suppress logging, then act accordingly
            if not settings["doLog_global"] or not settings[className]["doLog"]:
                return False
            else:
                return self._doLog

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

"""
Old tests

with open('sample.txt') as infile:
    str_sampleText = infile.readline()
    arr_sampleText = core.Encode(str_sampleText)

    if doLog_global:
        print(f"str_sampleText size:\t{len(str_sampleText)}")


class UnUtils(LogTest):

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


class UnEncrypt(LogTest):
    def test_encodeAndDecode_noMap(self):

        arr_encoded = core.Encode(str_sampleText)
        str_decoded = core.Decode(arr_encoded)
        self.assertEqual(str_sampleText, str_decoded)

    def test_EncodeAndDecode_withMap(self):
        """Tests Encode() and Decode() for an inverting map"""

    def test_VigenereA(self):
        pass

def RunTest(filename: str, classname: str):

    suite = unittest.TestSuite(obj_unTests)
    unittest.TextTestRunner(verbosity=0).run(suite)

"""