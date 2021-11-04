"""This script demonstrates the speed of PyCrypt's encryption by encrypting a plaintext copy of ___ and  printing the execution time"""

import database
from core import *
import time

# Add map to database if needed
if len(database.con.run("""SELECT 1 FROM maps WHERE "name"='alphaLower'""")) == 0:
    transform = {
        "A":0,  "a":0,  "B":1,  "b":1,  "C":2,  "c":2,  "D":3,  "d":3,  "E":4,  "e":4,
        "F":5,  "f":5,  "G":6,  "g":6,  "H":7,  "h":7,  "I":8,  "i":8,  "J":9,  "j":9,
        "K":10, "k":10, "L":11, "l":11, "M":12, "m":12, "N":13, "n":13, "O":14, "o":14,
        "P":15, "p":15, "Q":16, "q":16, "R":17, "r":17, "S":18, "s":18, "T":19, "t":19,
        "U":20, "u":20, "V":21, "v":21, "W":22, "w":22, "X":23, "x":23, "Y":24, "y":24,
        "Z":25, "z":25}

    t = DecompressTransform(transform)[0] 
    i = GenInverseTransform(t)
    inverse = CompressInverse(i)

    keywords = ["alpha", "lower", "ascii", "alphabet"]

    database.SaveMap("alphaLower", transform, inverse, keywords)

# Add cipher to database if needed
if len(database.con.run("""SELECT 1 FROM ciphers WHERE "name"='vigenere'""")) == 0:

    keywords = ["vigenere","caesar","polyalphabetic"]
    options = {"cycleKeywordOutsideMap": False, "deleteTextOutsideMap": True}

    formulaStr = """
assert len(mapRange) == 1 + max(mapRange)

if options["cycleKeywordOutsideMap"]:
    offset = np.resize(keys[0], len(text))[mappedIndices]

else:
    offset = np.resize(keys[0], len(mappedIndices))

out = (text[mappedIndices] + offset) % len(mapRange)

if not options["deleteTextOutsideMap"]:
    text[mappedIndices] = out
    out = text
"""

    inverseStr = """
assert len(mapRange) == 1 + max(mapRange)

if options["cycleKeywordOutsideMap"]:
    offset = np.resize(keys[0], len(text))[mappedIndices]
else:
    offset = np.resize(keys[0], len(mappedIndices))

if options["deleteTextOutsideMap"]:
    out = (text - offset) % len(mapRange)
else:
    out = (text[mappedIndices] - offset) % len(mapRange)

    text[mappedIndices] = out
    out = text
"""
    database.SaveCipher("vigenere", formulaStr, inverseStr, keywords, options)

mapQuery = database.LoadMap("alphaLower")
cipherQuery = database.LoadCipher("vigenere")

transform, mapRange = DecompressTransform(mapQuery[3])
inverse, inverseRange = DecompressInverse(mapQuery[4])


with open("Moby-Dick.txt", encoding="utf8") as infile:
    plaintext = infile.read()

keyword = "lemon"

keys = ProcessKeys(transform, keyword)
numRepr = Encode(plaintext)

mappedText, maskedIndices = ApplyTransform(numRepr, transform)

options = {"deleteTextOutsideMap": False, "cycleKeywordOutsideMap": False}

print("begin encryption")
t = time.time()
encryptedText = ApplyFormula(cipherQuery[3], mappedText, keys, mapRange, maskedIndices, options=options)
print(f"time to encrypt Moby Dick: {time.time()-t} sec.\nChars encrypted: {len(encryptedText)}")
print()
