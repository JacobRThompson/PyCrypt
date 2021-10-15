"""Python script that preforms all heavy lifting for PyArray.dll"""

__version__ = "1.0"
__author__ = "Jacob Thompson"

# TODO: DISTINGUISH BETWEEN TEXT AND NONTEXT KEYS; APPLY MAP TO STRING KEYS
#USER MUST BE USING LATER THAN PYTHON 3.7 FOR ORDERED DICTS

import numpy as np
from numpy.core.numeric import indices
import security

import time

emptyTransform = np.full(1114112, -1, dtype=np.int64)

def Encode(plaintext: str) -> np.ndarray:
    """ Converts passed string to int array"""
    return np.frombuffer(plaintext.encode("utf32"), dtype=np.int32)[1:]


def Decode(numRepr: np.ndarray) -> str:
    return numRepr.tobytes().decode("utf32")


def CompressTransform(transform: np.ndarray) -> dict[str, int]:

    indices = np.flatnonzero(transform >= 0)
    values = transform[indices]
    keys = Decode(indices)[::2]     #I Have no idea why \x00 gets added. Nonetheless we filter them out
    return {key: value for key, value in zip(keys, values)}


def DecompressTransform(transform: dict[str, int]):
    out = np.copy(emptyTransform)

    domain = Encode("".join(transform.keys()))
    range = tuple(transform.values())

    np.put(out, domain, range)
    return out, set(domain), set(range)


def GenInverseTransform(transform: np.ndarray) -> np.ndarray:

    out = np.copy(emptyTransform)
    range = np.flatnonzero(transform >= 0)
    domain = transform[range]

    np.put(out, domain, range)
    return out


def GenInverseMask(x, mask):
    return np.delete(np.arange(x.shape[0]), mask)


def PreprocessKeys(transform, *keys):
    keysOut = []

    # NOTE: WE CAN ENCODE IN ALL KEYS IN ONE STEP IF PERFORMANCE BECOMES BAD
    for key in keys:
        if type(key) != str:
            keysOut.append(key)

        else:
            k, m = ApplyTransform(Encode(key), transform)
            keysOut.append(np.delete(k, m))

        return keysOut


def ApplyTransform(numRepr: np.ndarray, transform: np.ndarray, maskedIndices=None):

    values = transform[numRepr]

    if maskedIndices is None:
        indices = np.flatnonzero(values == -1)
    else:
        indices = np.union1d(maskedIndices, np.flatnonzero(values == -1))

    np.put(values, indices, numRepr[indices])

    return values, indices

def ApplyFormula(formula, text, keys, mapRange, mappedIndices, options,
    pp=security.ProcParser("text", "keys", "mapRange", "mappedIndices", "options")):

    formula = "".join(("import numpy as np\n", formula))
    pp.EvalSafety(formula)

    _localsVars = {}
    exec(formula, {}, _localsVars)

    return _localsVars['out']



if __name__ == '__main__' and True:

    t = {
        "A":0,  "a":0,  "B":1,  "b":1,  "C":2,  "c":2,  "D":3,  "d":3,  "E":4,  "e":4,
        "F":5,  "f":5,  "G":6,  "g":6,  "H":7,  "h":7,  "I":8,  "i":8,  "J":9,  "j":9,
        "K":10, "k":10, "L":11, "l":11, "M":12, "m":12, "N":13, "n":13, "O":14, "o":14,
        "P":15, "p":15, "Q":16, "q":16, "R":17, "r":17, "S":18, "s":18, "T":19, "t":19,
        "U":20, "u":20, "V":21, "v":21, "W":22, "w":22, "X":23, "x":23, "Y":24, "y":24,
        "Z":25, "z":25}


    p = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!\t!ThE qUiCk BrOwN dOg JuMpEd OvEr ThE LaZy FoX!\t!abcdefghijklmnopqrstuvwxyz"

    transform = DecompressTransform(t)[0]
    tCheck = CompressTransform(transform)

    plaintext = Encode(p)

    inverse = GenInverseTransform(transform)

    plaintext, mask = ApplyTransform(plaintext, transform)
    plaintext = ApplyTransform(plaintext, inverse, mask)[0]

    temp = Decode(plaintext)

    print(temp)
    

def GenPlaintext(length=5000):
    return np.random.randint(0, 1114112, length, dtype=np.int32)

def GenKeywords(n, length=25):
    return [np.random.randint(0, 1114112, length, dtype=np.int32) for i in range(n)]

