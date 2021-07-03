"""Python script that preforms all heavy lifting for PyArray.dll"""

import numpy as np
import utils


def InverseTrans(transform: np.ndarray) -> np.ndarray:
    inv = np.zeros(transform.max()+1)
    return np.put(inv, transform, np.arange(len(transform)))


def Encode(plaintext: str, map: dict = None) -> np.ndarray:
    """ Converts passed string to int array; transform output one is given."""

    arr_unmapped = np.frombuffer(plaintext.encode("utf32"), dtype=np.int32)
    if map:
        # remove elements that are outside of map's domain
        arr_inDomain = np.in1d(arr_unmapped, map["domain"])
        temp = arr_unmapped[arr_inDomain]

        # Apply mapping. Also return any data needed to restore text
        return map["transform"][temp], arr_unmapped, arr_inDomain

    else:
        return arr_unmapped


def Decode(unmapped: np.ndarray, map: dict = None) -> str:

    # Apply inverse mapping if map is given
    temp = map["inverse"][unmapped] if map else unmapped
    return temp.tobytes().decode("utf32")


def Restore(unmapped: np.ndarray, original: np.ndarray,
            inDomain: np.ndarray, map: dict) -> str:

    # Preform inverse mapping
    arr_encoded = map["inverse"][unmapped]

    temp = np.copy(original)

    # Reassign values that were intially within the map's domain
    temp[inDomain] = arr_encoded

    return temp.tobytes().decode("utf32")


def Encrypt(plaintext: str, cipher=None, map=None, *keywords,
            usePresets: bool = True):

    if usePresets:
        cipher, map = utils.LoadPreset(cipher, map)

    utils.Validate(cipher, map)

    return exec(formula)





if __name__ == '__main__' and True:
    import unit_tests
