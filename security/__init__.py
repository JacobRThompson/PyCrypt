import ast
import json
import time
#TODO: ADD FUNCTIONALITY FOR CLASSES

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
        self._flaggedNodes = []
        
    def match(self, obj):

        #def IsChildBranch(subset,superset):
        #   return all (subset[i] is superset[i] for i in range(len(subset)))

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

                elif type(target) in (ast.Tuple, ast.List):
                    names = [item.id for item in target.elts]
                    self.AddSymbols(names, "__var_name__")
                    print(f"{', '.join(names)} were assigned")

                elif type(target) == ast.Subscript:
                    pass

        elif objType == ast.Attribute:

            nodeTree, searchTree = self.GenTree(obj)

            if searchTree[-1] in symbolTags:
                # We are calling a class method if this triggers. because python
                # is not strongly typed, we cannot determine what class is
                # calling this method. We assume it passes and that the user
                # has checked and is wary of the module in which the calling
                # class was defined

                print(f"Attribute {searchTree[0]} was accessed")
                return

            doPassSecurity = False

            for node, name in zip(nodeTree, searchTree):

                if name in self.whitelist:
                    doPassSecurity = True

                elif name in self.blacklist and doPassSecurity:
                    self._flaggedNodes.append(node)

                elif name in self.blacklist:

                    if any(node is flaggedNode for flaggedNode in self._flaggedNodes):
                        doPassSecurity = True
                    else:
                        raise AttributeError(
                            f"Invalid attribute '{searchTree[0]}'. '{name}' and "
                            f"all of its children are currently blacklisted."
                        )

            if not doPassSecurity:
                raise AttributeError(
                    f"Invalid attribute '{searchTree[0]}'. It is not in the "
                    f"current whitelist nor is it a child of any item on the "
                    f"current whitelist."
                )

            print(f"Attribute {searchTree[0]} was accessed")

        elif objType == ast.Call:
            # Occurs when we are calling a locally-defined function
            if type(obj.func) == ast.Name:
                functionName = obj.func.id
                print(f"{functionName} was called")
                assert functionName in self.symbols

        elif objType == ast.FunctionDef:
            funcName = obj.name
            self.AddSymbols(funcName, "__func_name__")
            print(f"function {funcName} was defined")
            # add function to whitelist so the user can call that function
            # without raising exceptions

        elif objType == ast.Import:
            importName = obj.names[-1].name
            importAlias = obj.names[-1].asname

            # THIS IS REDUNDANT!!!
            # self.AddSymbols(importName, importAlias)

            # check if import is on the whitelist
            # print(f"{importName} imported as {importAlias}")

        elif objType == ast.ImportFrom:
            baseModule = obj.module
            origName = obj.names[0].name
            alias = obj.names[0].asname

            # self.AddSymbols(f"{baseModule}.{origName}", alias)

            # print(f"imported {origName} from {baseModule} as {alias}")
            # check if import is on the whitelist

        else:
            #print(obj)
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

    def GenTree(self, obj) -> tuple[list, list]:

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

        #print(ast.dump(temp, indent =4))
        temp = ast.walk(temp)
        for i in temp:
            self.match(i)
       


print("-------------------------")


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

t=time.time()
temp = ProcParser()
temp.EvalSafety(string)

print(f"Time taken: {time.time()-t}")

if __name__ == "__main__" and False:
    pass
