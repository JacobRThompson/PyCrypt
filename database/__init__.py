
import json
import pg8000
import numpy as np

from security import hash

# validCiphers, validMaps = [], []
con: pg8000.Connection = None


def init() -> pg8000.Connection:

    global con

    with open("config.JSON", 'r') as config:
        settings = json.load(config)["general"]
        portNo = settings["TCPPort"]

    try:
        con = pg8000.connect(
            user="pycrypt_default_user", database="pycrypt", port=portNo,
            password="123")

    except pg8000.dbapi.ProgrammingError:

        # Used for testing purposes to avoid constant retyping of password
        # TODO: IMPLEMENT PROPER SYSTEM
        with open("C:/Users/jacob/Desktop/postgreSQL_password.txt", 'r') as infile:
            password = infile.readline()

        # connect as a superuser so we can create things as needed
        _con = pg8000.connect(user='postgres', password=password, port=portNo)

        with open("database/queryDoCreateDB.SQL", 'r') as infile:
            doCreateDB = _con.run(infile.read())[0][0]

        if doCreateDB:
            # Make sure we are not inside a transaction (It's jank. see pg8000
            # docs for more info)
            _con.rollback()
            _con.autocommit = True
            _con.run("CREATE DATABASE pycrypt")
            _con.autocommit = False

        with open("database/initUser.SQL", 'r') as infile:
            _con.run(infile.read())

            # TODO: Query if extension is available & create procedure for install

            _con.commit()
        _con.close

        # Connect to DB so we can modify it
        _con = pg8000.connect(
            user='postgres', database="pycrypt", password=password,
            port=portNo)

        with open("database/initDB.SQL", 'r') as infile:
            _con.run(infile.read())
            _con.commit()
        _con.close()

        # Reconnect with lower privileges
        # TODO: GIVE DEFAULT USER A TERRIBLE PASSWORD
        con = pg8000.connect(
            user="pycrypt_default_user", database="pycrypt", port=portNo,
            password="123")

    return con


def LoadPreset(cipher=None, map=None) -> list:
    assert cipher is None or type(cipher) == str
    assert map is None or type(map) == str
    assert con  # Make sure that we initalized module

    if map:
        mapQuery = con.run(f"SELECT * FROM maps WHERE map_name ={map}")[0]
        assert mapQuery is not None
    else:
        mapQuery = None

    if cipher:
        cipherQuery = con.run(f"SELECT * FROM ciphers WHERE cipher_name={cipher}")[0]
        assert cipherQuery is not None

        # If cipher has a listed map dependency...
        if cipherQuery[1] is not None:
            # and if the user passed a map query...
            if mapQuery:
                # we make sure the passed query and cipher dependency are one
                # and the same
                assert cipherQuery[1] == mapQuery[0]
            else:
                # otherwise we look up the listed dependency
                mapQuery = con.run(f"SELECT * FROM maps WHERE map_id = {cipherQuery[1]}")[0]
    else:
        cipherQuery = None

    # Validate hashes of retrieved cipher and/or map
    if mapQuery:
        assert hash.GenHash(mapQuery) == mapQuery[2]
    if cipherQuery:
        assert hash.GenHash(cipherQuery) == cipherQuery[3]

    # TODO VALIDATE CIPHER FORMULA
    
    return (cipherQuery, mapQuery)

def SavePreset(cipher=None, map=None, overwrite=True):

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

    '''
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
    '''
    
init()

print("Done. Somehow.")
