
import json
import pg8000
import numpy as np

import security

tempCiphers, tempMaps = {}, {}
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

def LoadSavedata(cipher=None, map=None) -> list:
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
    else:
        cipherQuery = None

    if mapQuery:
        # Validate hash
        assert security.GenHash(mapQuery[2:]) == mapQuery[1]

    if cipherQuery:
        # Validate hash
        assert security.GenHash(cipherQuery[2:]) == cipherQuery[1]

        # Make sure that cipher formula and inverse isn't malicious
        security.EvalSafety(cipherQuery[3])
        security.EvalSafety(cipherQuery[4])

    return (cipherQuery, mapQuery)


def SaveCipher(name, formula, inverse, keywords, options):

    hash_ = security.GenHash([name, formula, inverse, keywords, options])
    queryArgs = (hash_, name, formula, inverse, keywords, options)
    con.run(f"INSERT INTO ciphers VALUES {queryArgs}")


def SaveMap(name, transform, inverse, keywords):
   
    hash_ = security.GenHash([name, transform, inverse, keywords])
    queryArgs = (hash_, name, transform, inverse, keywords)
    con.run(f"INSERT INTO maps {queryArgs}")



    

init()

print("Done. Somehow.")
