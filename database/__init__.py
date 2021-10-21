import json
import pg8000
import getpass
import numpy as np
import sys,os

sys.path.insert(1, os.path.abspath('.'))
import security
import core

con: pg8000.Connection = None

# TODO: add check for proper table formating, even if database already exists

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
        password = getpass.getpass()

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

        # give user privileges to newly-created tabels    
        _con.run("GRANT SELECT, UPDATE, INSERT ON ciphers, maps TO pycrypt_default_user")
        _con.commit()
        _con.close()

        # Reconnect with lower privileges
        # TODO: GIVE DEFAULT USER A TERRIBLE PASSWORD
        con = pg8000.connect(
            user="pycrypt_default_user", database="pycrypt", port=portNo,
            password="123")

    return con

"""
def LoadNamedData(cipher=None, map=None) -> list:
    assert cipher is None or type(cipher) == str
    assert map is None or type(map) == str
    assert con  # Make sure that we initalized module

    if map:
        mapQuery = con.run(f"SELECT * FROM maps WHERE map_name ={map} LIMIT 1")[0]
        assert mapQuery is not None
    else:
        mapQuery = None

    if cipher:
        cipherQuery = con.run(f"SELECT * FROM ciphers WHERE cipher_name={cipher} LIMIT 1")[0]
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

    return (cipherQuery, mapQuery)"""

def SaveMap(name, transform, inverse, keywords):

    # Generate inverse transform if one is not provided
    if inverse is None:
        trans = core.DecompressTransform(transform)[0]
        inv = core.GenInverseTransform(trans)
        inverse = core.CompressInverse(inv)

    # Add escape characters so SQL insert doesn't break
    name = name.replace("'", "''")

    jTransform = json.dumps(transform)
    jInverse = json.dumps(inverse)

    queryStr = f"('{name}','{jTransform}','{jInverse}', ARRAY{keywords})"
    columnStr = """("name", transform, inverse, keywords)"""

    id = con.run(f"""INSERT INTO maps {columnStr} VALUES {queryStr} RETURNING id""")[0][0]
    data = con.run(f"""SELECT * FROM maps WHERE id = {id}""")[0]
    hash_ = security.GenHash(data[0], *data[2:])

    con.run(f"""UPDATE maps SET "hash" = ARRAY{hash_} WHERE id = {id}""")
    con.commit()


def SaveCipher(name, formula, inverse, keywords, options):

    jOptions = json.dumps(options)

    # Add escape characters to formulas so SQL insert doesn't break
    name = name.replace("'", "''")
    formula = formula.replace("'", "''")
    inverse = inverse.replace("'", "''")

    queryStr = f"('{name}','{formula}','{inverse}', ARRAY{keywords},'{jOptions}')"
    columnStr = """("name", formula, inverse, keywords, options)"""

    id = con.run(f"""INSERT INTO ciphers {columnStr} VALUES {queryStr} RETURNING id""")[0][0]
    data = con.run(f"""SELECT * FROM ciphers WHERE id = {id}""")[0]
    hash_ = security.GenHash(data[0], *data[2:])

    con.run(f"""UPDATE ciphers SET "hash" = ARRAY{hash_} WHERE id = {id}""")
    con.commit()


def LoadMap(identifier):

    if type(identifier) == int:
        query = con.run(f"""SELECT * FROM maps WHERE id = {identifier}""")
    elif type(identifier) == str:
        query = con.run(f"""SELECT * FROM map WHERE "name" = '{identifier}'""")
    else:
        raise TypeError(f"Identifier must be an integer or a string. A {type(identifier)} was given instead.")

    for entry in query:
        if entry[1] != security.GenHash(entry[0], *entry[2:]):
            raise Exception(f"Hash discrepancy found")

    # format output
    return query[0] if len(query) == 1 else query

def LoadCipher(identifier):

    if type(identifier) == int:
        query = con.run(f"""SELECT * FROM ciphers WHERE id = {identifier}""")
    elif type(identifier) == str:
        query = con.run(f"""SELECT * FROM ciphers WHERE "name" = '{identifier}'""")
    else:
        raise TypeError(f"Identifier must be an integer or a string. A {type(identifier)} was given instead.")

    for entry in query:
        if entry[1] != security.GenHash(entry[0], *entry[2:]):
            raise Exception(f"Hash discrepancy found")

    # format output
    return query[0] if len(query) == 1 else query

def LoadMap(identifier):

    if type(identifier) == int:
        query = con.run(f"""SELECT * FROM maps WHERE id = {identifier}""")
    elif type(identifier) == str:
        query = con.run(f"""SELECT * FROM maps WHERE "name" = '{identifier}'""")
    else:
        raise TypeError(f"Identifier must be an integer or a string. A {type(identifier)} was given instead.")

    for entry in query:
        if entry[1] != security.GenHash(entry[0], *entry[2:]):
            raise Exception(f"Hash discrepancy found")

    # format output
    return query[0] if len(query) == 1 else query

init()
