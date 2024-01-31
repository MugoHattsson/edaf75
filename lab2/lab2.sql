-- Delete the tables if they exist.
-- Disable foreign key checks, so the tables can
-- be dropped in arbitrary order.
PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS theaters;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS performances;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS memberships;

PRAGMA foreign_keys=ON;

-- Create the tables.
CREATE TABLE theaters (
    theater_name    TEXT,
    capacity        INT,
    PRIMARY KEY     (theater_name),
);

CREATE TABLE customers (
    user_name       TEXT,
    full_name       TEXT,
    password        TEXT,
    PRIMARY KEY     (user_name)
);

CREATE TABLE movies (
    imdb            TEXT,
    titel           TEXT,
    year            INT,
    runtime         INT,
    PRIMARY KEY     (imdb)
);

CREATE TABLE performances (
    performance_id  TEXT DEFAULT (lower(hex(randomblob(16)))),
    start_time      TIME,
    theater_name    TEXT,
    imdb            TEXT,
    PRIMARY KEY     (performance_id),
    FOREIGN KEY     (theater_name) REFERENCES theaters(theater_name),
    FOREIGN KEY     (imdb) REFERENCES movies(imdb)          
);

CREATE TABLE tickets (
    ticket_id       TEXT DEFAULT (lower(hex(randomblob(16)))),
    user_name       TEXT,
    performance_id  TEXT,
    PRIMARY KEY     (ticket_id),
    FOREIGN KEY     (user_name) REFERENCES customers(user_name),
    FOREIGN KEY     (performance_id) REFERENCES performances(performance_id)
);
-- Insert data into the tables.
-- INSERT
-- INTO    ... (...)
-- VALUES  (...);

