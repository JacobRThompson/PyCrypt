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


def DecompressTransform(transform: dict[str, int]):
    out = np.copy(emptyTransform)

    domain = Encode("".join(transform.keys()))
    range = tuple(transform.values())

    np.put(out, domain, range)
    return out, set(range)


def DecompressInverse(inverse: dict[int, int]):
    out = np.copy(emptyTransform)

    domain = tuple(inverse.keys())
    range = tuple(inverse.values())

    np.put(out, domain, range)
    return out, set(range)


def CompressTransform(transform: np.ndarray) -> dict[str, int]:

    indices = np.flatnonzero(transform >= 0)
    values = transform[indices]
    keys = Decode(indices)[::2]     #I Have no idea why \x00 gets added. Nonetheless we filter them out
    return {key: value for key, value in zip(keys, values.tolist())}


def CompressInverse(inverse: np.ndarray) -> dict[int, int]:

    indices = np.flatnonzero(inverse >= 0)
    values = inverse[indices]
    
    return {int(key): value for key, value in zip(indices.tolist(), values.tolist())}


def GenInverseTransform(transform: np.ndarray) -> np.ndarray:

    out = np.copy(emptyTransform)
    range = np.flatnonzero(transform >= 0)
    domain = transform[range]

    np.put(out, domain, range)
    return out

def GenInverseMask(x, mask):
    return np.delete(np.arange(x.shape[0]), mask)


def ProcessKeys(transform, *keys):
    keysOut = []

    # NOTE: WE CAN ENCODE IN ALL KEYS IN ONE STEP IF PERFORMANCE BECOMES BAD
    for key in keys:
        if type(key) != str:
            keysOut.append(key)

        else:
            # if key is a string, cast it to array of ints by encoding
            k, m = ApplyTransform(Encode(key), transform)

            # we discard characters that fall outside the transform (maybe we
            # can make this toggleable in the future)
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

def ApplyFormula(formula, text, keys, mapRange, maskedIndices, options={}):
    # Keys need to be processed before hand
    # TODO add better functionality for auto-importing modules

    pp = security.ProcParser("text", "keys", "mapRange", "mappedIndices", "maskedIndices", "options", numpy="np")
    pp.EvalSafety(formula)

    mappedIndices = np.delete(np.arange(len(text)), maskedIndices)

    _localsVars = {
        "keys": keys, "options": options, "text": text, "mapRange": mapRange,
        "mappedIndices": mappedIndices, "maskedIndices": maskedIndices
    }
    exec(formula, {"np": np},  _localsVars)

    return _localsVars['out']


def GenPlaintext(length=5000):
    return np.random.randint(0, 1114112, length, dtype=np.int32)

def GenKeywords(n, length=25):
    return [np.random.randint(0, 1114112, length, dtype=np.int32) for i in range(n)]

