
IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = 'pycrypt_default_user') THEN
    CREATE USER 'pycrypt_default_user' WITH NOCREATEDB NOCREATEUSER;
END IF;
