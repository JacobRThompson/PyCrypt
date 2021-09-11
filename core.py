"""Python script that preforms all heavy lifting for PyArray.dll"""

__version__ = "1.0"
__author__ = "Jacob Thompson"

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
    return out


def DecompressEqualities(equality: dict[str, str]):
    out = np.copy(emptyTransform)

    domain = Encode("".join(equality.keys()))
    range = Encode("".join(equality.values()))

    np.put(out, domain, range)
    return out


def GenInverseTransform(transform: np.ndarray) -> np.ndarray:

    out = np.copy(emptyTransform)
    range = np.flatnonzero(transform >= 0)
    domain = transform[range]

    np.put(out, domain, range)
    return out


def ApplyTransform(numRepr: np.ndarray, transform: np.ndarray, maskedIndices=None):

    values = transform[numRepr]

    if maskedIndices is None:
        indices = np.flatnonzero(values == -1)
    else:
        indices = np.union1d(maskedIndices, np.flatnonzero(values == -1))

    np.put(values, indices, numRepr[indices])

    return values, indices


if __name__ == '__main__' and True:

    t = {
        "A":0,  "b":1,  "C":2,  "d":99,  "E":4,  "f":5,  "G":6,  "h":7,  "I":8,  "j":9,
        "K":10, "l":11, "M":12, "n":13, "O":14, "p":15, "Q":16, "r":17, "S":18, "t":19,
        "U":20, "v":21, "V":22, "w":23, "X":24, "y":25, "Z":26}

    e = {
        "B":"b", "D":"d", "F":"f", "H":"h", "J":"j",
        "L":"l", "N":"n", "P":"p", "R":"r", "T":"t",
        "V":"v", "W":"w", "Y":"y"
    }


    p = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!\t!THE QUICK BROWN DOG JUMPED OVER THE LAZY FOX!\t!abcdefghijklmnopqrstuvwxyz"

    #t0 = time.time()
    transform = DecompressTransform(t)
    t2 = CompressTransform(transform)

    equalities = DecompressEqualities(e)

    plaintext = Encode(p)

    inverse = GenInverseTransform(transform)

    plaintext = ApplyTransform(plaintext, equalities)[0]
    plaintext, mask = ApplyTransform(plaintext, transform)
    plaintext = ApplyTransform(plaintext, inverse, mask)[0]

    temp = Decode(plaintext)

    #print(time.time()-t0)
    print(temp)


def GenPlaintext(length=5000):
    return np.random.randint(0, 1114112, length, dtype=np.int32)

def GenKeywords(n, length=25):
    return [np.random.randint(0, 1114112, length, dtype=np.int32) for i in range(n)]