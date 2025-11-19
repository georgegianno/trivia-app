DO $do$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'trivia_db_owner') THEN
        CREATE ROLE trivia_db_owner WITH LOGIN ENCRYPTED PASSWORD 'NA0;z3-b3£0@';
    END IF;
    ALTER ROLE trivia_db_owner WITH LOGIN ENCRYPTED PASSWORD 'NA0;z3-b3£0@';
END
$do$;
ALTER ROLE trivia_db_owner SET CLIENT_ENCODING='UTF-8';
CREATE DATABASE trivia_db ENCODING 'UTF-8' OWNER trivia_db_owner;
