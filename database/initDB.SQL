DO $$    
BEGIN
	CREATE EXTENSION IF NOT EXISTS pg_trgm;
    IF NOT EXISTS (
		SELECT FROM information_schema.tables
		WHERE table_schema = 'public'
		AND	table_name = 'maps')
	THEN
        CREATE TABLE maps(
            id          INT GENERATED ALWAYS AS IDENTITY,
            "hash"      INTEGER[],
            "name"      TEXT NOT NULL,
            
            transform   JSON NOT NULL,
            inverse     JSON NOT NULL,

            keywords    TEXT[],

			PRIMARY KEY (id)
        );

        CREATE INDEX idx_map_name ON maps USING GIN ("name" gin_trgm_ops);
        CREATE INDEX idx_map_keywords ON maps USING GIN (keywords);
		
    END IF;
	
	IF NOT EXISTS (
		SELECT FROM information_schema.tables
		WHERE table_schema = 'public'
		AND	table_name = 'ciphers')
	THEN
        CREATE TABLE ciphers(
            id          INT GENERATED ALWAYS AS IDENTITY,
            "hash"      INTEGER[],
            "name"      TEXT NOT NULL,
            
            formula     TEXT NOT NULL,    
            inverse     TEXT NOT NULL,

            keywords    TEXT[],
            options     JSON,
            
			PRIMARY KEY (id)
            
        );

        CREATE INDEX idx_cipher_name ON ciphers USING GIN ("name" gin_trgm_ops); 
        CREATE INDEX idx_cipher_keywords ON ciphers USING GIN (keywords);
    END IF;
END 
$$;