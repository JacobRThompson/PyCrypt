from os import path

import json
import pickle
import sqlite3

import numpy as np

# Move to parent directory to make getting files cleaner
path.chdir(path.abspath('..')) 

# ------------------------------------------------------------------------------
# SQL\Database Settup

def InitDB(*args, **kwargs) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    """ Connects to a database using the passed args/kwargs. Then formats DB by
    creating cipher and map table if they do not already exist. Returns
    connection and cursor objects used to access database"""

    con = sqlite3.connect(*args,**kwargs)
    cur = con.cursor()
    with open("init_db.SQL", "r") as infile:
        cur.executescript(infile.read())
        con.commit()

    return con, cur

# Register python datatypes (dict, set, np.ndarray) for DB use
pkl = lambda obj: pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

sqlite3.register_adapter(dict      , pkl)
sqlite3.register_adapter(set       , pkl)
sqlite3.register_adapter(np.ndarray, pkl)

sqlite3.register_converter("py_dict"   , pickle.loads)
sqlite3.register_converter("py_set"    , pickle.loads)
sqlite3.register_converter("py_ndarray", pickle.loads)

# Create Temporary DB that will hold all validated ciphers\maps
con_mem, cur_mem = InitDB("file::memory:?cache=shared")

# Create save data DB if it does not exist
with open ("config.JSON",'r') as infile:
    dbPath = json.load(infile)["general"]["dbPath"]
    if not path.exists(dbPath)
    InitDB(dbPath)

# End of SQL Setup
# ------------------------------------------------------------------------------


def LoadPreset(cipher=None, map=None, path="presets.JSON") -> list:
    with open(path, 'r') as infile:
        saveData = json.load(infile)

        out = []
        if type(cipher) == str:
            # put saveData into dataframe so we can search through it easier
            df_c = pd.DataFrame.from_records(saveData["ciphers"])

            out.append(df_c.loc[df_c['name'] == cipher])

        # if a dict is passed as a parameter, we assume it contains usable
        # data for a cipher and pass it through.
        elif type(cipher) == dict:
            out.append(cipher)

        elif not cipher:
            out.append(None)
        else:
            raise TypeError()

        if type(map) == str:
            # put saveData into dataframe so we can search through it easier
            df_m = pd.DataFrame.from_records(saveData["maps"])

            out.append(df_m.loc[df_m['name'] == map])

        # if a map is passed as a parameter, we assume it contains usable
        # data for a cipher and pass it through.
        elif type(map) == dict:
            out.append(map)

        elif not map:
            out.append(None)
        else:
            raise TypeError


def SavePreset(cipher=None, map=None, path="presets.JSON", overwrite=True):

    if cipher:
        pass

    if map:
        pass

    pass


def Validate(cipher=None, map=None, textLen=5000, keywordLen=25):
   
   # TODO: add check that cipher/map is either dict or NoneType

    if cipher not in prevCiphers:
        # Generate completely random unicode string
        arr_plaintext = np.random.randint(0, 1114112, textLen, dtype = np.int32)

        # Generate minimum number of keywords to use cipher
        list_keywords = [np.random.randint(0, 1114112, keywordLen, dtype = np.int32)\
                         for i in range(cipher["noKeywords"])]

        # Create and format copies of the generated plaintext and keywords that
        # the cipher can play with without breaking everything
        text = arr_plaintext.copy()
        keywords = [key.copy() for key in list_keywords]

        arr_encrypted = exec(cipher["formula"])

        # Reassign values so we can decrypt text
        text = arr_encrypted.copy()
        keywords = [key.copy() for key in list_keywords]

        arr_decrypted = exec(cipher["inverse"])

        # If data is lost/changed, raise exception
        assert np.array_equal(arr_decrypted, arr_plaintext)

        # Record cipher if it passes all tests
        prevCiphers.append(cipher)

    if map not in prevMaps:
        pass

