""" This should fail due to explicitly importing moduleA.subModuleA on blacklist"""
from moduleA import subModuleB, subModuleA