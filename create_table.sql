-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;
-- GRANT ALL ON SCHEMA public TO postgres;
-- GRANT ALL ON SCHEMA public TO public;

CREATE TABLE lifts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE cycles (
    id SERIAL PRIMARY KEY,
    start_date TIMESTAMP,
    number integer UNIQUE
);

CREATE TABLE lift_increments (
    id SERIAL PRIMARY KEY,
    lift TEXT REFERENCES lifts(name),
    increment NUMERIC(10,2) NOT NULL
);

CREATE TABLE cycle_lift_max (
    id SERIAL PRIMARY KEY,
    lift TEXT REFERENCES lifts(name),
    amount NUMERIC(10,2) NOT NULL,
    cycle_num INTEGER REFERENCES cycles(number)
);

CREATE TABLE cycle_lift_weekly (
    id SERIAL PRIMARY KEY,
    week INTEGER CHECK (week < 5),
    lift TEXT REFERENCES lifts(name),
    amount NUMERIC(10,2) NOT NULL,
    reps INTEGER CHECK (reps < 6),
    percentage INTEGER NOT NULL,
    reps_achieved INTEGER,
    cycle_num INTEGER REFERENCES cycles(number)
);
