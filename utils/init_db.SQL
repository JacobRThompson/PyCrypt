    
BEGIN;

CREATE TABLE IF NOT EXISTS ciphers(
    cipher_id   INTEGER PRIMARY KEY,

    "name"      TEXT,
    "hash"      TEXT,
    pickle      BLOB,

    keywords    INTEGER DEFAULT 0,
    formula     TEXT,    
    inverse     TEXT  
);


CREATE TABLE IF NOT EXISTS maps(
    map_id      INTEGER PRIMARY KEY,

    "name"      TEXT,
    "hash"      TEXT,
    pickle      BLOB,

    keywords    INTEGER DEFAULT 0,
    transform   py_ndarray,
    inverse     py_ndarray,
    domain      py_set,
    "range"     py_set,
    equalities  py_dict
);

COMMIT;
