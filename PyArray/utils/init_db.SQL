-- Script for setting up database of  ciphers and maps 

CREATE TABLE IF NOT EXISTS ciphers(
    cipher_name     TEXT PRIMARY KEY,
    no_keywords     INTEGER DEFAULT 0,

    cipher_formula  TEXT,    
    cipher_inverse  TEXT
        
);

CREATE TABLE IF NOT EXISTS maps(
    map_name        TEXT PRIMARY KEY,
    no_keywords     INTEGER DEFAULT 0,

    map_transform   py_ndarray,
    map_inverse     py_ndarray,
    map_domain      py_set,
    map_range       py_set,
    equalities_id   py_dict
);

