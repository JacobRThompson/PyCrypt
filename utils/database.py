from os import path

import json
import pickle
import sqlite3

import numpy as np

validCiphers, validMaps = [], []

# will contain sets of the form: {pickle.dumps(cipher), pickle.dumps(map)}
# to signify valid cipher/map combinations that only work with each other
validCombo = []

pickles ={}
# Move to parent directory to make getting files cleaner
path.chdir(path.abspath('..'))

# ------------------------------------------------------------------------------
# SQL\Database Settup

def InitDB(*args, **kwargs) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    """ Connects to a database using the passed args/kwargs. Then formats DB by
    creating cipher and map table if they do not already exist. Returns
    connection and cursor objects used to access database"""

    con = sqlite3.connect(*args, **kwargs)
    cur = con.cursor()
    with open("init_db.SQL", "r") as infile:
        cur.executescript(infile.read())
        con.commit()

    return con, cur

# Register python datatypes (dict, set, np.ndarray) for DB use
def _Pkl(obj): return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

sqlite3.register_adapter(dict      , _Pkl)
sqlite3.register_adapter(set       , _Pkl)
sqlite3.register_adapter(np.ndarray, _Pkl)

sqlite3.register_converter("py_dict"   , pickle.loads)
sqlite3.register_converter("py_set"    , pickle.loads)
sqlite3.register_converter("py_ndarray", pickle.loads)

# Connect/create DB containing savedata
with open("config.JSON", 'r') as infile:
    dbPath = json.load(infile)["general"]["dbPath"]
    con_disk, cur_disk = InitDB(dbPath)

# End of SQL Setup
# ------------------------------------------------------------------------------


def LoadPreset(cipher=None, map=None, path=dbPath) -> list:
   
    out = []
    if type(cipher) == str:

        cur_disk.execute(f"SELECT * FROM ciphers WHERE cipher_name = '{cipher}'\
                         LIMIT 1")
        result = cur_disk.fetchone()
        if result:
            out.append(result)
        else:
            raise KeyError(f"Cannot find cipher named '{cipher}' in {dbPath}")

    # If a dict is passed as a parameter, we assume it contains usable
    # data for a cipher and pass it through.
    elif type(cipher) == dict:
        out.append(cipher)
    elif not cipher:
        out.append(None)
    else:
        raise TypeError(f"Passed cipher '{cipher}' is neither a str or NoneType")

    if type(map) == str:

        cur_disk.execute(f"SELECT * FROM maps WHERE map_name = '{map}'\
                         LIMIT 1")
        result = cur_disk.fetchone()
        if result:
            out.append(result)
        else:
            raise KeyError(f"Cannot find map named '{map}' in {dbPath}")

    # If a dict is passed as a parameter, we assume it contains usable
    # data for a map and pass it through.
    elif type(cipher) == dict:
        out.append(cipher)
    elif not map:
        out.append(None)
    else:
        raise TypeError(f"Passed map '{map}' is neither a str or NoneType")

    return out


def SavePreset(cipher=None, map=None, path="presets.JSON", overwrite=True):

    if cipher:
        pass

    if map:
        pass

    pass


def Validate(cipher=None, map=None, textLen=5000, keywordLen=25):

    def EvalCommand(command, text, keywords):
        """ Evaluates passed cipher/map command in a scope where it can
        manipulate variable without breaking the calling function"""

        #NOTE: THIS IS EXTREMELY UNSAFE!!! DON'T BE AN IDIOT ABOUT IT
        #WE CAN FIX THIS BY PARSING STRING INTO OBJECTS (ast module will help)
        return exec(command)

    # TODO: Check map/cipher combinations first

    if map not in validMaps:
        pass
        #TODO: use difflib.ndiff to compare strings 


    if cipher not in validCiphers:
        # Generate completely random unicode string
        plaintext = np.random.randint(0, 1114112, textLen, dtype=np.int32)

        # Generate minimum number of keywords to use cipher
        keywords = [np.random.randint(0, 1114112, keywordLen, dtype=np.int32)
                    for i in range(cipher["noKeywords"])]

        # Create and format copies of the generated plaintext and keywords that
        # the cipher can play with without breaking everything

        encryptedText = EvalCommand(cipher["cipher_formula"], plaintext,
                                    keywords)

        decryptedText = EvalCommand(cipher["cipher_inverse"], plaintext,
                                    keywords)

        # If data is lost/changed, raise exception.
        # TODO: if map passed validation, Try again using mapping/demapping
        # this time. If it  
        assert np.array_equal(plaintext, decryptedText)

        # Record cipher if it passes all tests
        validCiphers.append(cipher)

    