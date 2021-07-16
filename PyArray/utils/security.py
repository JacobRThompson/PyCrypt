import ast
import numpy as np


def evalSafety(cmd: str):
    temp = ast.parse(cmd)
    print(ast.dump(temp,indent=4))

    print("---------------------------------------")

    for i in ast.walk(temp):

        # If the user attempts to call a function, we make sure that it is in
        # the list of approved funcs

        if type(i) == ast.Call:
            funcName = i.func.attr
            funcModule = i.func.value.id
            print(f"{funcModule}.{funcName} was called")

        # Check if the user is trying to import anything
        if type(i) == ast.Import:
            print("!!!")


        print(i)

string = '''
import sys as s
def Test(x):
    return np.arange(x)
a = np.array([[1,2,3],[4,5,6],[7,8,9]])
b = np.sum(a,axis=0)+5
'''

evalSafety(string)


