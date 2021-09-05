""" This should pass """

# Can we reassign variable by importing module?
moduleA = 5
import moduleA

# Can we alias module as blacklisted Name?
import moduleA as moduleE 

# Can we have multiple imports at once?
import moduleA, moduleB.subModuleB, moduleC.subModuleC.subSubModuleC

# Can we use import from to skip blacklisted modules?
from moduleB import subModuleB, subModuleA

# Does the last test work when we alias?
from moduleB import subModuleA as subA, subModuleB as subB
