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
    PRIMARY KEY     (theater_name)
);

CREATE TABLE customers (
    user_name       TEXT,
    full_name       TEXT,
    password        TEXT,
    PRIMARY KEY     (user_name)
);

CREATE TABLE memberships (
    theater_name    TEXT,
    user_name       TEXT,
    PRIMARY KEY     (theater_name, user_name),
    FOREIGN KEY     (theater_name) REFERENCES theaters(theater_name),
    FOREIGN KEY     (user_name) REFERENCES customers(user_name)
);

CREATE TABLE movies (
    imdb            TEXT,
    title           TEXT,
    year            INT,
    run_time        INT,
    PRIMARY KEY     (imdb)
);

CREATE TABLE performances (
    performance_id  TEXT DEFAULT (lower(hex(randomblob(16)))),
    start_time      TIME,
    date            DATE,
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
INSERT
INTO    theaters(theater_name, capacity)
VALUES  ('Filmstaden Lund', 500),
        ('Kino', 200);

INSERT
INTO    customers(user_name, full_name, password)
VALUES  ('mugohattsson', 'Hugo Mattsson', '12345'),
        ('empa', 'Emelie Bondesson', '9876');

INSERT
INTO    movies(imdb, title, year, run_time)
VALUES  ('abc', 'Forrest Gump', 2003, 120),
        ('def', 'Mamma Mia', 2010, 135);
        
INSERT
INTO    performances(start_time, date, theater_name, imdb)
VALUES  ('18:00', '2024-02-05', 'Filmstaden Lund', 'abc'),
        ('20:00', '2024-02-05', 'Filmstaden Lund', 'def'),
        ('15:00', '2024-04-08', 'Filmstaden Lund', 'abc'),
        ('19:00', '2024-04-08', 'Filmstaden Lund', 'def'),
        ('20:00', '2024-02-05', 'Kino', 'abc'),
        ('13:00', '2024-03-06', 'Kino', 'def'),
        ('10:00', '2024-03-06', 'Kino', 'abc'),
        ('23:00', '2024-02-05', 'Kino', 'def');
