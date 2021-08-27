import ast
import json

symbolTags = ("__func_name__", "__var_name__")

class ProcParser:

    def __init__(self):

        with open("config.JSON", 'r') as config:
            settings = json.load(config)["security"]

        self.useSecurity = settings["useSecurity"]
        self.whitelist = set(settings["whitelist"])
        self.blacklist = set(settings["blacklist"])
        self.symbols = {}

    def match(self, obj):

        objType = type(obj)

        if objType == ast.alias:
            origName = obj.name
            alias = obj.asname

            self.AddSymbols(origName, alias)

            print(f"{origName} aliased as {alias}")

        elif objType == ast.Assign:
            for target in obj.targets:
                if type(target) == ast.Name:
                    name = target.id
                    self.AddSymbols(name, "__var_name__")
                    print(f"{name} was assigned")

                elif type(target in (ast.Tuple, ast.List)):
                    names = [item.id for item in target.elts]

                    self.AddSymbols(names, "__var_name__")
                    print(f"{', '.join(names)} were assigned")

        elif objType == ast.Attribute:

            # get a breakdown of modules/submodule any called function is from.
            currentNode = obj
            moduleTree = []

            while currentNode:
                if type(currentNode) == ast.Attribute:
                    moduleTree.append(currentNode.attr)
                    currentNode = currentNode.value

                # Triggers when we are at base module (ex. "numpy" in numpy.matlib.ones)   
                elif type(currentNode) == ast.Name:

                    baseModule = currentNode.id
                    assert baseModule in self.symbols

                    # de-alias if necessary
                    if self.symbols[baseModule]:
                        baseModule = self.symbols[baseModule]

                    moduleTree.append(baseModule)
                    currentNode = None
                else:
                    currentNode = None
                    return

            moduleTree.reverse()

            self.VerifyAttribute(moduleTree)
            print(f"Attribute {'.'.join(moduleTree)} was accessed")

        elif objType == ast.Call:
            # Occurs when we are calling a locally-defined function
            if type(obj.func) == ast.Name:
                functionName = obj.func.id
                print(f"{functionName} was called")
                assert functionName in self.symbols

        elif objType == ast.FunctionDef:
            funcName = obj.name
            self.AddSymbols(funcName, "__func_name__")
            # print(f"function {funcName} was defined")
            # add function to whitelist so the user can call that function
            # without raising exceptions

        elif objType == ast.Import:
            importName = obj.names[-1].name
            importAlias = obj.names[-1].asname

            # THIS IS REDUNDANT!!!
            # self.AddSymbols(importName, importAlias)

            # check if import is on the whitelist
            print(f"{importName} imported as {importAlias}")

        elif objType == ast.ImportFrom:
            baseModule = obj.module
            origName = obj.names[0].name
            alias = obj.names[0].asname

            # self.AddSymbols(f"{baseModule}.{origName}", alias)

            print(f"imported {origName} from {baseModule} as {alias}")
            # check if import is on the whitelist

        else:
            # print(obj)
            pass

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

    def VerifyAttribute(self, moduleTree: list):

        # This occurs if we are calling a user-defined attribute
        if moduleTree[0] in symbolTags:
            return

        isWhitelist = False

        currentString = moduleTree[0]
        assert currentString not in self.blacklist
        isWhitelist = True if currentString in self.whitelist else isWhitelist

        # Iteratively go through modules in tree and check blacklist/whitelist
        # status. If numpy isn't blacklisted, what about numpy.load etc.?
        for substring in moduleTree[1:]:
            currentString = ".".join((currentString,substring))
            assert currentString not in self.blacklist
            isWhitelist = True if currentString in self.whitelist else isWhitelist    

        assert isWhitelist

    def EvalSafety(self, cmd: str, *args):
        temp = ast.parse(cmd, *args)
        temp = ast.walk(temp)
        for i in temp:
            self.match(i)

print("-------------------------")

string = '''
import numpy as np
import numpy as nump
import os


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
'''
# TODO: WORK OUT WAY TO MAKE SURE Z.REVERSE() ISN'T SUSPECT

temp=ProcParser()
temp.EvalSafety(string)

if __name__ == "__main__" and False:
    pass
