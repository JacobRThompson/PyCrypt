DO $$
BEGIN
    IF NOT EXISTS(
        SELECT FROM pg_roles WHERE rolname = 'pycrypt_default_user') 
    THEN
        CREATE USER pycrypt_default_user WITH PASSWORD '123';
    END IF;
END $$;





