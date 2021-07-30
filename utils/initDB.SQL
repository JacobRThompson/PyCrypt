    
BEGIN;

    CREATE TABLE IF NOT EXISTS ciphers(
        cipher_id   SERIAL NOT NULL PRIMARY KEY,

        "name"      TEXT,
        "hash"      TEXT,
        pickle      TEXT NOT NULL,
        keywords    json,

        formula     TEXT NOT NULL,    
        inverse     TEXT  
    );

    CREATE TABLE IF NOT EXISTS maps(
        map_id      SERIAL NOT NULL PRIMARY KEY,
        cipher_id   INTEGER,
        
        "name"      TEXT,
        "hash"      TEXT,
        pickle      TEXT,
        keywords    json,

        transform   json NOT NULL,
        inverse     json NOT NULL,
        domain      json,
        "range"     json,
        equalities  json
    );

COMMIT;
