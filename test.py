import database

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
        out = np.put(text, mappedIndices, out)
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
        out = np.put(text, mappedIndices, out)
    """

    database.SaveCipher("vigenere", formulaStr, inverseStr, keywords, options)

query  = database.LoadCipher("vigenere")
print("done")