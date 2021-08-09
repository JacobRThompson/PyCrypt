DO $$    
BEGIN
	CREATE EXTENSION IF NOT EXISTS pg_trgm;
	
    IF NOT EXISTS (
		SELECT FROM information_schema.tables
		WHERE table_schema = 'public'
		AND	table_name = 'maps')
	THEN
        CREATE TABLE maps(
            map_id      INT GENERATED ALWAYS AS IDENTITY,
            
            map_name        TEXT,
            map_hash        TEXT,
            map_pickle      TEXT,
            map_keywords    TEXT[],

            map_transform   JSON NOT NULL,
            map_inverse     JSON NOT NULL,
            map_domain      INTEGER[],
            map_range       INTEGER[],
            map_equalities  INTEGER[],
			
			PRIMARY KEY (map_id)
        );

        CREATE INDEX idx_map_name ON maps USING GIN (map_name gin_trgm_ops);
        CREATE INDEX idx_map_keywords ON maps USING GIN (map_keywords);
		
    END IF;
	
	IF NOT EXISTS (
		SELECT FROM information_schema.tables
		WHERE table_schema = 'public'
		AND	table_name = 'ciphers')
	THEN
        CREATE TABLE ciphers(
            cipher_id       INT GENERATED ALWAYS AS IDENTITY,
            map_id          INT,

            cipher_name     TEXT,
            cipher_hash     TEXT,
            cipher_pickle   TEXT,
            cipher_keywords TEXT[],

            cipher_formula  TEXT NOT NULL,    
            cipher_inverse  TEXT,  

            
			PRIMARY KEY (cipher_id),
            CONSTRAINT cipher_map
                FOREIGN KEY(map_id) REFERENCES maps(map_id)
        );

        CREATE INDEX idx_cipher_name ON ciphers USING GIN (cipher_name gin_trgm_ops); 
        CREATE INDEX idx_cipher_keywords ON ciphers USING GIN (cipher_keywords);
    END IF;
END 
$$;