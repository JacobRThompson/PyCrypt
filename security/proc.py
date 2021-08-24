import ast

def evalSafety(cmd: str):

    temp = ast.parse(cmd, type_comments=True)

    switch = SwitchHandler()
    # print(ast.dump(temp, indent=4))
    print("---------------------------------------")

    temp = ast.walk(temp)

    for i in temp:
        switch.match(i)

    """
    demonstration of how to forcibly get next value from generator
    for i in temp:
        switch.match(i)
        try:
            j = next(temp)
        except:
            pass
    """

symbolTags = ("__func_name__","__var_name__")

class SwitchHandler:

    def __init__(self, whitelist=set(), blacklist=set(), symbols={}):
        self.blacklist = blacklist
        self.whitelist = whitelist
        self.symbols = symbols

        # Dict describing what functions to call for each datatype that can be
        # passed to self.match() 
        self.cases = {
            ast.alias: self._alias,
            ast.Assign: self._Assign,
            ast.Attribute: self._Attribute,
            ast.Call: self._Call,
            ast.FunctionDef: self._FunctionDef,
            ast.Import: self._Import,
            ast.ImportFrom: self._ImportFrom,
            "default": self._default}

    def match(self, obj):

        t = type(obj)
        if t in self.cases:
            return self.cases[t](obj)
        else:
            return self.cases["default"](obj)

    def _alias(self, obj: ast.alias):
        origName = obj.name
        alias = obj.asname

        self.AddSymbol(origName, alias)

        print(f"{origName} aliased as {alias}")

    def _Assign(self, obj: ast.Assign):
        name = obj.targets[0].id
        self.AddSymbol(name, "__var_name__")

        print(f"{name} was assigned")

    def _Attribute(self, obj: ast.Attribute):

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

                print("\tnon-name, non-attribute :", end="")
                currentNode = None

        moduleTree.reverse()
        print(f"Attribute {'.'.join(moduleTree)} was accessed")

    def _Call(self, obj: ast.Call):

        #moduleTree = GetAttributeModules(obj.func)
        #print(f"{'.'.join(moduleTree)} was called using {id(obj.func)}")

        # If the user attempts to call a function, we make sure that it is in
        # the list of approved funcs
        pass
    
    def _FunctionDef(self, obj: ast.FunctionDef):
        funcName = obj.name
        self.AddSymbol(funcName, "__func_name__")
        # print(f"function {funcName} was defined")
        # add function to whitelist so the user can call that function
        # without raising exceptions

    def _Import(self, obj: ast.Import):
        importName = obj.names[-1].name
        importAlias = obj.names[-1].asname

        # THIS IS REDUNDANT!!!
        # self.AddSymbol(importName, importAlias)

        # check if import is on the whitelist
        # print(f"{importName} imported as {importAlias}")

    def _ImportFrom(self, obj: ast.ImportFrom):
        baseModule = obj.module
        origName = obj.names[0].name
        alias = obj.names[0].asname

        # self.AddSymbol(f"{baseModule}.{origName}", alias)

        # print(f"imported {origName} from {baseModule} as {alias}")
        # check if import is on the whitelist

    def _default(self, obj):
        # print(obj)
        pass
    
    def AddSymbol(self, name, alias=None):
        alias = str(alias) if alias else None
        name = str(name)

        if alias in symbolTags:
            self.symbols[name] = alias
        elif alias:
            self.symbols[alias] = name
        else:
            self.symbols[name] = None


string = '''
import pandas
import numpy as np
import numpy as nump
import os.path

from numpy.matlib import ones
from os.path import abspath as osPathAbspath


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

y+z

z=a
q=z

test = 132
'''
# TODO: WORK OUT WAY TO MAKE SURE Z.REVERSE() ISN'T SUSPECT

evalSafety(string)

# TODO:
# -add blacklisted names for assignment (np, etc)
# -add blacklisted functions that raise a special exception
# -keep track of lambda functions
# -method for evaluating if function is whitelisted
# deal with multiple assignment
if __name__ == "__main__" and False:
    pass
