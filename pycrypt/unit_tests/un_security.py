import unittest
import json
from . import LogTest
from utils import security





class UnValidate(LogTest):
    pass





suite = unittest.TestSuite(UnValidate(doLog=True))
unittest.TextTestRunner(verbosity=0).run(suite)