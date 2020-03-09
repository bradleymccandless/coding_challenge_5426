import random
from django.test import TestCase,Client

def set_up_screens():
    data = {}
    # Variety. It is the spice of life.
    # The Kinepolis-Madrid Ciudad de la Imagen megaplex in Spain 
    # is the largest movie theater in the world, with 25 screens...
    screens = random.randint(1, 25)
    for screen in range(1, screens+1):
         # ...and a seating capacity of 9,200 including a 996-seat auditorium.
         # https://en.wikipedia.org/wiki/Multiplex_(movie_theater)
         seats = random.randint(1, 996)
         data[str(screen)] = {'seats': seats, 'movies': {}}
         Client().post('/api/screens', {'seats': seats}, 'application/json')
    return(data)

def set_up_movies(screen_data):
    data = {}
    # we could generate fake EIDR Content ID's here. but I'll just count.
    movie_id = 1
    for screen in screen_data:
        # average movie length is 96.5 minutes. with 1440 minutes in 24 hours
        # maybe we show up to 15 movies per screen 
        movies = random.randint(1, 15)
        for movie in range(1, movies+1):
            hour = str(random.randint(0, 23)).zfill(2)
            minute = str(random.randint(0, 59)).zfill(2)
            data[str(movie_id)] = {
                'showtime': hour+':'+minute+':00',
                'screen_id': int(screen),
                'purchased_seats': 0,
                'on_sale': False
            }
            movie_id += 1
            Client().post('/api/movies', {'screen': int(screen), 'showtime': hour+':'+minute}, 'application/json')
    return(data)

def sell_some_tickets(movie_data):
    for movie in movie_data:
        # flip a coin. does it go on sale?
        on_sale = random.randint(0, 1)
        if on_sale == True:
            movie_data[movie]['on_sale'] = True
            Client().put('/api/tickets', {'movie': int(movie)}, 'application/json')
    return(movie_data)

class ScreenTest(TestCase):    
    def test_screens(self):
        screen_data = set_up_screens()
        response = Client().get('/api/screens')
        self.assertEqual(response.json(), screen_data)
    def test_screen_bad_requests(self):
        seats = random.randint(1, 996)
        response = Client().put('/api/screens', {'seats': seats}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().delete('/api/screens', {'seats': seats}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().patch('/api/screens', {'seats': seats}, 'application/json')
        self.assertEqual(response.status_code, 400)
    def test_screen_bad_json(self):
        seats = random.randint(1, 996)
        response = Client().post('/api/screens', {'seatz': seats}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/screens', {'seats': 'seats'}, 'application/json')
        self.assertEqual(response.status_code, 400)
    def test_screen_bounds(self):
        response = Client().post('/api/screens', {'seats': 0}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/screens', {'seats': 997}, 'application/json')
        self.assertEqual(response.status_code, 400)
    
class MovieTest(TestCase):
    def test_movies(self):
        screen_data = set_up_screens()
        movie_data = set_up_movies(screen_data)
        response = Client().get('/api/movies')
        self.assertEqual(response.json(), movie_data)
    def test_movie_bad_requests(self):
        screen_data = set_up_screens()
        response = Client().put('/api/movies', {'screen': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().delete('/api/movies', {'screen': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().patch('/api/movies', {'screen': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
    def test_movie_bad_json(self):
        screen_data = set_up_screens()
        response = Client().post('/api/movies', {'screem': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/movies', {'screen': 'screen'}, 'application/json')
        self.assertEqual(response.status_code, 400)
        screen_data = set_up_screens()
        response = Client().post('/api/movies', {'screen': 1, 'showtime': 2}, 'application/json')
        self.assertEqual(response.status_code, 400)
    def test_movie_bounds(self):
        screen_data = set_up_screens()
        response = Client().post('/api/movies', {'screen': 0}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/movies', {'screen': 26}, 'application/json')
        self.assertEqual(response.status_code, 400)

class ScreenMovieTest(TestCase):
    def test_screens_movies(self):
        screen_data = set_up_screens()
        movie_data = set_up_movies(screen_data)
        screen_movie_data = screen_data
        for screen in screen_data:
            for movie in movie_data:
                if movie_data[movie]['screen_id'] == int(screen):
                    screen_movie_data[screen]['movies'][movie] = movie_data[movie]
        for screen in screen_movie_data:
            for movie in screen_movie_data[screen]['movies']:
                screen_movie_data[screen]['movies'][movie].pop('screen_id')
        response = Client().get('/api/screens')
        self.assertEqual(response.json(), screen_movie_data)

class TicketTest(TestCase):
    def test_sell_some_tickets(self):
        screen_data = set_up_screens()
        movie_data = set_up_movies(screen_data)
        movie_data = sell_some_tickets(movie_data)
        response = Client().get('/api/movies')
        self.assertEqual(response.json(), movie_data)
    def test_purchase_tickets(self):
        screen_data = set_up_screens()
        movie_data = set_up_movies(screen_data)
        movie_data = sell_some_tickets(movie_data)
        for movie in movie_data:
            if movie_data[movie]['on_sale'] == True:
                amount = random.randint(1, screen_data[str(movie_data[movie]['screen_id'])]['seats'])
                movie_data[movie]['purchased_seats'] = amount
                response = Client().post('/api/tickets', {'movie': int(movie), 'amount': amount}, 'application/json')
        response = Client().get('/api/movies')
        self.assertEqual(response.json(), movie_data)
    def test_ticket_bad_requests(self):
        screen_data = set_up_screens()
        movie_data = set_up_movies(screen_data)
        response = Client().get('/api/tickets')
        self.assertEqual(response.status_code, 400)
        response = Client().delete('/api/tickets', {'movie': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().patch('/api/tickets', {'movie': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
    def test_ticket_bad_json(self):
        screen_data = set_up_screens()
        movie_data = set_up_movies(screen_data)
        response = Client().put('/api/tickets', {'movle': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().put('/api/tickets', {'movie': '1'}, 'application/json')
        self.assertEqual(response.status_code, 400)
        # ensure movie 1 is for sale
        Client().put('/api/tickets', {'movie': 1}, 'application/json')
        response = Client().post('/api/tickets', {'mov1e': 1, 'amount': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/tickets', {'movie': '1', 'amount': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/tickets', {'movie': 1, 'amount': '1'}, 'application/json')
        self.assertEqual(response.status_code, 400)
    def test_ticket_bounds(self):
        screen_data = set_up_screens()
        movie_data = set_up_movies(screen_data)
        movie_data = sell_some_tickets(movie_data)
        # ensure movie 1 is for sale
        Client().put('/api/tickets', {'movie': 1}, 'application/json')
        response = Client().post('/api/tickets', {'movie': 0, 'amount': 1}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/tickets', {'movie': 1, 'amount': 0}, 'application/json')
        self.assertEqual(response.status_code, 400)
        response = Client().post('/api/tickets', {'movie': 1, 'amount': 997}, 'application/json')
        self.assertEqual(response.status_code, 400)
