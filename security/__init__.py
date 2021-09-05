import ast
import json
import time
# TODO: ADD FUNCTIONALITY FOR CLASSES
# IMPORTS F DOES NOT FAIL!!!
symbolTags = (
    "__func_name__", "__var_name__", "__class_instance__"
)

class ProcParser:

    def __init__(self):

        with open("config.JSON", 'r') as config:
            settings = json.load(config)["security"]

        self.useSecurity = settings["useSecurity"]
        self.whitelist = set(settings["whitelist"])
        self.blacklist = set(settings["blacklist"])

        self.symbols = {}
  
    def Walk(self, obj):

        objType = type(obj)

        if objType == ast.alias:

            origName = obj.name
            alias = obj.asname
            self.AddSymbols(origName, alias)
            # print(f"{origName} aliased as {alias}")


        elif objType == ast.Assign:

            for target in obj.targets:
                if type(target) == ast.Name:
                    name = target.id
                    self.AddSymbols(name, "__var_name__")
                    # print(f"{name} was assigned")

                elif type(target) in (ast.Tuple, ast.List):
                    names = [item.id for item in target.elts]
                    self.AddSymbols(names, "__var_name__")
                    # print(f"{', '.join(names)} were assigned")

                elif type(target) == ast.Subscript:
                    pass


        elif objType == ast.Attribute:
            # Shortcut to the end of attribute chain so we don't have to
            # evaluate intermediate attributes multiple times

            nodeTree, searchTree = self.CollectAttributeChain(obj)
            self.EvalAttributeChain(searchTree)
            obj = nodeTree[-1]


        elif objType == ast.Call:
            # Occurs when we are calling a locally-defined function
            if type(obj.func) == ast.Name:
                functionName = obj.func.id
                # # print(f"{functionName} was called")
                # maybe check if local function has __func_name__ tag?
                assert functionName in self.symbols


        elif objType == ast.FunctionDef:
            funcName = obj.name
            self.AddSymbols(funcName, "__func_name__")
            # print(f"function {funcName} was defined")


        elif objType in (ast.Import, ast.ImportFrom):

            if objType == ast.Import:
                importName = obj.names[-1].name
                # importAlias = obj.names[-1].asname
            else:
                importName = ".".join((obj.module, obj.names[0].name))
                # importAlias = obj.names[0].asname

            treeStrings = importName.split(".")
            searchTree = ['.'.join(treeStrings[:i]) for i in range(len(treeStrings), 0, -1)]

            self.EvalAttributeChain(searchTree, errorType=ImportError)


        for child in ast.iter_child_nodes(obj):
            self.Walk(child)


    def AddSymbols(self, name, alias=None):

        if type(name) == str:

            assert name not in symbolTags, (
                f"{name} as a string is used internally by ProcParser. Parsed "
                "Functions, variables, etc. cannot use this name.")

            alias = alias if alias else None
            if alias in symbolTags:
                self.symbols[name] = alias
            elif alias:
                self.symbols[alias] = name
            else:
                self.symbols[name] = None

        elif type(name) in (list, tuple):
            for i in name:
                self.AddSymbols(i, alias)

    def EvalAttributeChain(self, searchTree, errorType=AttributeError):
        
        # We are calling a class method if this fails to triggers. because
        # python is not strongly typed, we cannot determine what class is
        # calling this method. We assume it passes and that the user has
        # checked and is wary of the module in which the calling class was
        # defined
        if searchTree[-1] not in symbolTags:

            doFailSecurity = True

            for name in searchTree:

                if name in self.whitelist:
                    doFailSecurity = False

                elif name in self.blacklist and doFailSecurity:
                    raise errorType(
                        f"Invalid attribute '{searchTree[0]}'. '{name}' and "
                        f"all of its children are currently blacklisted."
                    )
                
            if doFailSecurity:
                raise errorType(
                    f"Invalid attribute '{searchTree[0]}'. It is not in the "
                    f"current whitelist nor is it a child of any item on the "
                    f"current whitelist."
                )
        # print(f"Attribute {searchTree[0]} was accessed")
        

    def CollectAttributeChain(self, obj) -> tuple[list, list]:

        currentNode = obj
        nodeTree = []
        treeStrings = []

        while currentNode:
            if type(currentNode) == ast.Attribute:

                nodeTree.append(currentNode)
                treeStrings.append(currentNode.attr)
                currentNode = currentNode.value

            # Triggers when we are at base module (ex. "numpy" in numpy.matlib.ones) 
            elif type(currentNode) == ast.Name:
                nodeTree.append(currentNode)
                treeStrings.append(self.DeAlias(currentNode.id))
                currentNode = None

            # Triggers when we find a class obj calling a mehtod
            elif type(currentNode) == ast.Call:
                nodeTree.append(currentNode)
                treeStrings.append("__class_instance__")
                currentNode = None

            else:
                currentNode = None

        treeStrings.reverse()
        # create the search path used when evaluating blacklist and whitelist.
        # We always start at called attritbute and work through its parent modules
        # Ex: numpy.random.rand -> numpy.random -> numpy

        searchTree = ['.'.join(treeStrings[:i]) for i in range(len(treeStrings), 0, -1)]

        return nodeTree, searchTree

    def DeAlias(self, alias):
        if alias in self.symbols and self.symbols[alias]:
            return self.symbols[alias]
        else:
            return alias

    
    def EvalSafety(self, cmd: str, *args):
        temp = ast.parse(cmd, *args)

        self.Walk(temp)

# print("-------------------------")


# TODO: WORK OUT DICTS
# importing submodule does not necessarily import parent

string = '''
import numpy as np
import numpy as nump
from numpy.matlib import ones
def Test(x):
    return np.arange(x)
Test2 = lambda x: np.random.randn(x)
if 1>2:
    a = np.array([[1,2,3],[4,5,6],[7,8,9]])
    # assign B
    HELLO = np.sum(a,axis=0).T+5
else:
    a = Test2(5)
z=[1,2,3,4,5]
z.reverse()
y=np.array([[1,2],[3,4]])
Test(5)
y+z
Test2(3)
f = Test2(4)
g = Test(12)
a={1:"FOO",2:np.mat.mul(500)}
a[3]="once"
'''

temp = ProcParser()
temp.EvalSafety(string)

if __name__ == "__main__" and True:
    import unittest

    testWhitelist = {
        "moduleA",
        "moduleB.subModuleA",
        "moduleB.subModuleB",
        "moduleC.subModuleC.subSubModuleC"
    }
    testBlacklist = {
        "moduleA.subModuleA",
        "moduleB",
        "moduleE"
    }

    def evalTestFile(path):
        pp = ProcParser()
        pp.whitelist = testWhitelist
        pp.blacklist = testBlacklist
        with open(path,'r') as infile:
            cmd = infile.read()
        pp.EvalSafety(cmd)

    class EvalSafetyUnitTest(unittest.TestCase):

        def test_imports(self):
            evalTestFile("security/unitTests/importsA.py")

            self.assertRaises(ImportError,
                evalTestFile, "security/unitTests/importsB.py"
            )
            self.assertRaises(ImportError,
                evalTestFile, "security/unitTests/importsC.py"
            )
            self.assertRaises(ImportError,
                evalTestFile, "security/unitTests/importsD.py"
            )
            self.assertRaises(ImportError,
                evalTestFile,"security/unitTests/importsE.py"
            )
            self.assertRaises(ImportError,
                evalTestFile, "security/unitTests/importsF.py"
            )
            self.assertRaises(ImportError,
                evalTestFile, "security/unitTests/importsG.py"
            )

    unittest.main()

