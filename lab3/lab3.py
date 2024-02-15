import sqlite3
import hashlib
import os

from urllib.parse import unquote
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
    os.system('sqlite3 movies.sqlite < lab3.sql')

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
        query = """
            SELECT  *
            FROM    movies
            WHERE   TRUE
            """

        params = []

        if request.query.title:
            query += "AND title = ?"
            params.append(unquote(request.query.title))

        if request.query.year:
            query += "AND year = ?"
            params.append(request.query.year)

        c.execute(query, params)
        
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

    except sqlite3.IntegrityError as e:
        response.status = 400
        return str(e)

    else:
        db.commit()
        ticket_id, = found
        response.status = 201
        return f"/tickets/{ticket_id}"

@get('/users/<user_name>/tickets')
def get_user_tickets(user_name):
    c = db.cursor()
    c.execute(
        """
        WITH user_tickets(performance_id, count) as (
            SELECT   performance_id, count() as count
            FROM     tickets
            WHERE    user_name = ?
            GROUP BY performance_id
        )
        SELECT  date, 
                start_time, 
                theater_name, 
                title, 
                year, 
                count as nbrOfTickets

        FROM    user_tickets
                join performances using(performance_id)
                join movies using(imdb)
        """,
        [user_name]
    )

    found = [{'date': date,
          'startTime': start_time,
          'theater': theater_name,
          'title': title,
          'year': year,
          'nbrOfTickets': nbrOfTickets} for date, start_time, theater_name, title, year, nbrOfTickets in c]

    if not found:
        response.status = 400
        return "User has no tickets"

    response.status = 200

    return {'data': found}

run(host='localhost', port=PORT)
