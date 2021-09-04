""" This should pass """

# Can we reassign variable by importing module?
moduleA = 5
import moduleA
moduleA.subModuleC.func()

# Can we alias module as blacklisted Name?
import moduleA as moduleE 
moduleA.func()

# Can we have multiple imports at once?
import moduleA, moduleB.subModuleB, moduleC.subModuleC.subSubModuleC
moduleA.func()
moduleB.subModuleB.unknownSubSubModule.func()
#moduleC.subModuleC.subSubModuleC

# Can we use import from to skip blacklisted modules?
from moduleB import subModuleB, subModuleA
subModuleB
subModuleA

# Does the last test work when we alias?
from moduleB import subModuleA as subA, subModuleB as subB
subA
subB