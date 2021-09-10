
import json
import pg8000
import numpy as np

import security

tempCiphers, tempMaps = {}, {}
con: pg8000.Connection = None

#TODO: TRANSFORM QUERIES FROM LIST TO DICT

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

    if mapQuery:
        # Validate hash
        assert security.GenHash(mapQuery) == mapQuery[2]
        
    if cipherQuery:
        # Validate hash
        assert security.GenHash(cipherQuery) == cipherQuery[3]

        # Make sure that cipher formula and inverse isn't malicious
        security.EvalSafety(cipherQuery[5])
        security.EvalSafety(cipherQuery[6])
    
    return (cipherQuery, mapQuery)

def SavePreset(cipher=None, map=None, overwrite=True):

    if cipher:
        pass

    if map:
        pass

    pass

def SaveTemp():
    pass

def LoadTemp():
    pass


    

init()

print("Done. Somehow.")
