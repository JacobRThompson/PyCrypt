import os

import getpass
import json
import pickle
import pg8000

import numpy as np
username = getpass.getuser()

with open("config.JSON", 'r') as config:
    settings = json.load(config)["general"]
    dbPath = settings["dbPath"]
    dbName = settings["dbName"]
    portNo = settings["TCPPort"]
    doCreateDirectory = settings["doCreateDirectory"]
    del(settings)

# Move to parent directory to make getting files cleaner
os.chdir(os.path.abspath('.'))

validCiphers, validMaps = [], []

# For testing purposes to avoid constant retyping of password
with open("C:/Users/jacob/Desktop/postgreSQL_password.txt", 'r') as infile:
    password = infile.readline()

try:
    # con = pg8000.connect(user=username, database=dbName, port=portNo)
    con = pg8000.connect(user='postgres', password=password, database=dbName,
                         port=portNo)
    cur = con.cursor()

# if db does not exist, we create it
except: # TODO: FILTER EXCEPTIONS, DEAL WITH ALREADY EXISTING pyCrypt TABLESPACE

    if not os.path.isdir(dbPath) and doCreateDirectory:
        os.mkdir(dbPath)
    else:
        # If we don't create a new directory, we make sure that the new one is
        # empty or contains a database
        assert len(os.listdir(dbPath)) == 0,\
            f" Database '{dbName}' was not found, but its target directory \
            '{dbPath}' was.An attempt was made to load or create a database \
            here, but non-database files were found at {dbPath}."

    dbAbsPath = os.path.join(os.getcwd(), dbPath)

    con = pg8000.connect(user='postgres', password=password, port=portNo)

    # Turn on automommit so that we don't run the following in a transaction
    # (Which is not allowed by postgreSQL)
    con.autocommit = True
    con.run(f"CREATE TABLESPACE pyCrypt LOCATION '{dbAbsPath}'")
    con.run(f"CREATE DATABASE {dbName} WITH TABLESPACE = pyCrypt")
    con.autocommit = False
    con.close()

    # (Once implemented) reconnect with lower privileges so we don't accidentally
    # do something stupid
    con = pg8000.connect(user='postgres', password=password, database=dbName,
                         port=portNo)
    cur = con.cursor()

    with open("init_db.SQL", 'r') as infile:
        con.run(infile.read())

    cur = con.cursor()

def LoadPreset(cipher=None, map=None, path=dbPath) -> list:
   
    out = []
    if type(cipher) == str:

        cur.execute(f"SELECT * FROM ciphers WHERE cipher_name = '{cipher}'\
                         LIMIT 1")
        result = cur.fetchone()
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

        cur.execute(f"SELECT * FROM maps WHERE map_name = '{map}'\
                         LIMIT 1")
        result = cur.fetchone()
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

print("Done. Somehow.")