import sqlite3
import hashlib

from bottle import get, post, request, response, run

PORT = 7007
db = sqlite3.connect('movies.sqlite')

def hash(msg):
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

@get('/ping')
def ping():
    response.status = 200
    return 'pong'

@post('/reset')
def reset():

    c = db.cursor()
    try:
        c.execute('PRAGMA foreign_keys=OFF;')
        c.execute('DROP TABLE IF EXISTS theaters;')
        c.execute('DROP TABLE IF EXISTS customers;')
        c.execute('DROP TABLE IF EXISTS movies;')
        c.execute('DROP TABLE IF EXISTS performances;')
        c.execute('DROP TABLE IF EXISTS tickets;')
        c.execute('DROP TABLE IF EXISTS theaters;')
        c.execute('PRAGMA foreign_keys=ON;')

        c.execute(
            """
            CREATE TABLE theaters (
                theater_name    TEXT,
                capacity        INT,
                PRIMARY KEY     (theater_name)
            );
            """
        )
        c.execute(
            """
            CREATE TABLE customers (
                user_name       TEXT,
                full_name       TEXT,
                password        TEXT,
                PRIMARY KEY     (user_name)
            );
            """
        )
        c.execute(
            """
            CREATE TABLE movies (
                imdb            TEXT,
                title           TEXT,
                year            INT,
                PRIMARY KEY     (imdb)
            );
            """
        )
        c.execute(
            """
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
            """
        )
        c.execute(
            """
            CREATE TABLE tickets (
                ticket_id       TEXT DEFAULT (lower(hex(randomblob(16)))),
                user_name       TEXT,
                performance_id  TEXT,
                PRIMARY KEY     (ticket_id),
                FOREIGN KEY     (user_name) REFERENCES customers(user_name),
                FOREIGN KEY     (performance_id) REFERENCES performances(performance_id)
            );
            """
        )
        c.execute(
            """
            INSERT
            INTO    theaters(theater_name, capacity)
            VALUES  ('Kino', 10),
                    ('Regal', 16),
                    ('Skandia', 100);
            """
        )
        db.commit()

    except sqlite3.IntegrityError:
        response.status = 409
        return "Something went wrong"

@post('/users')
def post_user():
    user = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO    customers(user_name, full_name, password)
            VALUES  (?,?,?);
            """,
            [user['username'], user['fullName'], hash(user['pwd'])]
        )
    except sqlite3.IntegrityError:
        response.status = 400
        return ""
    else:
        db.commit()
        response.status = 201
        return f"/users/{user['username']}"


@post('/movies')
def post_movie():
    movie = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO    movies(imdb, title, year)
            VALUES  (?,?,?);
            """,
            [movie['imdbKey'], movie['title'], movie['year']]
        )
    except sqlite3.IntegrityError:
        response.status = 400
        return ""
    else:
        db.commit()
        response.status = 201
        return f"/movies/{movie['imdbKey']}"


@post('/performances')
def post_performance():
    performance = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO        performances(start_time, date, theater_name, imdb)
            VALUES      (?,?,?,?)
            RETURNING   performance_id
            """,
            [performance['time'], performance['date'], performance['theater'], performance['imdbKey']]
        )

        found = c.fetchone()
        if found:
            db.commit()
            response.status = 201
            performance_id, = found
            return f"/performances/{performance_id}"
                
    except sqlite3.IntegrityError:
        response.status = 400
        return ""


@get('/movies')
def get_movies():
    c = db.cursor()
    try:
        c.execute( """
            SELECT  *
            FROM    movies
            """
        )
        found = [{'imdbKey': imdb,
                 'title': title,
                 'year': year} for imdb, title, year in c]

        if not found:
            response.status = 400
            return "No such movies"
        else:
            response.status = 200
            return {'data': found}
    except sqlite3.IntegrityError:
        response.status = 400
        return ""

@get('/movies/<imdbKey>')
def get_movie_id(imdbKey):
    c = db.cursor()
    try:
        c.execute( """
            SELECT  *
            FROM    movies
            WHERE   imdb = ?
            """,
            [imdbKey]
        )
        found = [{'imdbKey': imdb,
                 'title': title,
                 'year': year} for imdb, title, year in c]

        if not found:
            response.status = 400
        else:
            response.status = 200

        return {'data': found}
    except sqlite3.IntegrityError:
        response.status = 400
        return ""

@get('/performances')
def get_performances():
    c = db.cursor()
    try:
        c.execute( """
            WITH taken_seats(performance_id, taken) as (
                SELECT performance_id, count() as taken
                FROM performances
                        JOIN theaters using(theater_name)
                        JOIN tickets using(performance_id)
                GROUP BY performance_id
            )
            SELECT  performance_id, 
                    date, 
                    start_time, 
                    title, 
                    year, 
                    theater_name, 
                    capacity - coalesce(taken, 0) as remaining_seats
            FROM performances
                    JOIN theaters using(theater_name)
                    JOIN movies using(imdb)
                    LEFT OUTER JOIN taken_seats using(performance_id)
            """
        )
        found = [{'performanceId': performance_id,
                 'date': date,
                 'startTime': start_time,
                  'title': title,
                  'year': year,
                  'theater': theater_name,
                  'remainingSeats': remaining_seats} for performance_id, date, start_time, title, year, theater_name, remaining_seats in c]

        if not found:
            response.status = 400
            return "No such performances"
        else:
            response.status = 200
            return {'data': found}
    except sqlite3.IntegrityError:
        response.status = 400
        return ""


@post('/tickets')
def post_ticket():
    ticket = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            WITH taken_seats(performance_id, taken) as (
                SELECT  performance_id, count() as taken
                FROM    performances
                        JOIN theaters using(theater_name)
                        JOIN tickets using(performance_id)
                GROUP BY performance_id
            )
            SELECT capacity - coalesce(taken, 0) as remaining_seats
            FROM    performances
                    JOIN theaters using(theater_name)
                    LEFT OUTER JOIN taken_seats using(performance_id)
            WHERE   performance_id = ?
            """,
            [ticket['performanceId']]
        )
        remaining, = c.fetchone()

        if remaining <= 0:
            response.status = 400
            return "No tickets left"

        c.execute(
            """
            SELECT  *
            FROM    customers
            WHERE   user_name = ? and password = ?
            """,
            [ticket['username'], hash(ticket['pwd'])]
        )
        user = c.fetchone()

        if not user:
            response.status = 401
            return "Wrong user credentials"

        c.execute(
            """
            INSERT
            INTO        tickets(user_name, performance_id)
            VALUES      (?,?)
            RETURNING   ticket_id
            """,
            [ticket['username'], ticket['performanceId']]
        )
        found = c.fetchone()

        if not found:
            response.status = 400
            return "Error"

        ticket_id, = found
        response.status = 201
        return f"/tickets/{ticket_id}"


    except sqlite3.IntegrityError:
        response.status = 400
        return "Error"
    else:
        db.commit()
        response.status = 201
        return ""


run(host='localhost', port=PORT)
