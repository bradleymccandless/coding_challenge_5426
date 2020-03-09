Let's say we have a movie theatre. The movie theatre can have the following things:
- Rooms with a designated capacity (number of seats)
- Movies that are playing at a set time every day
- Tickets that are sold to customers
The API should be able to do the following
- Set up rooms
- Set up movie showtimes
- Sell some tickets
- Look at the list of movie rooms and what they're playing
- Look at the list of movies playing at the theatre
- Buy tickets to a movie

What we're looking for is an API-only implementation of the service, written in Django. We are not looking for real payments, nor do we care about separating user roles - the API can be anonymous. We would like to see testing, though.

# Multiplex API Reference

Very simple, strictly JSON API.

### /api/screens
###### GET
A list of all the screening rooms and what movies are playing.
###### POST
Add a new screening room with {"seats": N} where N is the number of seats as an integer from 1 to 996.
### /api/movies
###### GET
A list of all the movies in the multiplex on sale and not on sale.
###### POST
Add a new movie with {"screen": N} where N is the screening room ID as an interger. Optionally {"screen": N, "showtime": "HH:MM"} set the showtime to something other than now().
### /api/tickets
###### PUT
Sell tickets to the {"movie": N} where N is the movie ID as an integer.
###### POST
Purchase a ticket to the {"movie": N} where N is the movie ID as an integer. Optionally buy more than one ticket {"movie": N, "amount": M} where M is an integer from 1 to (the number of free tickets remaining). 
# Run
```bash
python3 manage.py migrate
python3 manage.py test
python3 manage.py runserver
curl -X POST -H "ContentType: application/json" -d '{"seats":996}' http://localhost:8000/api/screens
curl -X POST -H "ContentType: application/json" -d '{"screen":1}' http://localhost:8000/api/movies
curl -X POST -H "ContentType: application/json" -d '{"screen":1, "showtime": "11:22"}' http://localhost:8000/api/movies
curl -X PUT -H "ContentType: application/json" -d '{"movie":1}' http://localhost:8000/api/tickets
curl -X PUT -H "ContentType: application/json" -d '{"movie":2}' http://localhost:8000/api/tickets
curl -X POST -H "ContentType: application/json" -d '{"movie":1}' http://localhost:8000/api/tickets
curl -X POST -H "ContentType: application/json" -d '{"movie":2, "amount": 996}' http://localhost:8000/api/tickets
```
Then view /api/screens and /api/movies in Firefox.
