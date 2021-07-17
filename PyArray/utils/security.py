import ast

import numpy as np

def evalSafety(cmd: str):

    temp = ast.parse(cmd, type_comments=True)

    switch = WalkSwitch()
    print(ast.dump(temp, indent=4))
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
class WalkSwitch:

    def __init__(self, whitelist=set(), aliases={}):
        self.whitelist = whitelist
        self.aliases = aliases

        self.cases = {ast.alias: self._alias, ast.Call: self._Call,
            ast.FunctionDef: self._FunctionDef, ast.Import: self._Import,
            ast.ImportFrom: self._ImportFrom, "default": self._default}

    def match(self, obj):

        t = type(obj)
        if t in self.cases:
            return self.cases[t](obj)
        else:
            return self.cases["default"](obj)

    def _alias(self, obj: ast.alias):
        origName = obj.name
        alias = obj.asname
  
        if alias and origName in self.aliases:
            self.aliases[origName].append(alias)
        elif alias:
            self.aliases[origName] = [alias]

        print(f"{origName} aliased as {alias}")

    def _Call(self, obj: ast.Call):
        funcName = obj.func.attr
        #funcModule = obj.func.value.id
        #print(f"{funcModule}.{funcName} was called")

        # If the user attempts to call a function, we make sure that it is in
        # the list of approved funcs

    def _FunctionDef(self, obj: ast.FunctionDef):
        funcName = obj.name
        print(f"function{funcName} was defined")
        # add function to whitelist so the user can call that function
        # without raising exceptions

    def _Import(self, obj: ast.Import):
        importName = obj.names[-1].name
        # check if import is on the whitelist
        print(f"{importName} imported")

    def _ImportFrom(self, obj: ast.ImportFrom):
        baseModule = obj.module
        print(f"imported a func from {baseModule}")
        # check if import is on the whitelist

    # TODO: Raise exception if the user tries to import or use "import from"
    # TODO: Raise exception if the user tries to define a class

    def _default(self, obj):
        print(obj)


string = '''
np.sum(np.random.randn(5).T)
'''



'''
def Test(x):
    return np.arange(x)

Test2 = lambda x: np.random.randn(x)

if 1>2:
    a = np.array([[1,2,3],[4,5,6],[7,8,9]])
    # assign B
    b = np.sum(a,axis=0).T+5

else:
    a = Test2(5) 

# def c
c=[a]
# def d
d=c
# def e
e=d

'''

evalSafety(string)


