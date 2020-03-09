from django.db import models

class Screen(models.Model):
    seats = models.PositiveSmallIntegerField(default=0)

# the primary key could also be the movie's EIDR Content ID
class Movie(models.Model):
    # we could have a one-to-many showtimes table for multiple screenings per day
    # and move purchased_seats in to each showtime
    # also a movie length field that a celery task would use
    # to reset the purchased_seats to zero once the screening ends
    # also use the length field to ensure no screen is double-booked
    showtime = models.TimeField()
    screen = models.ForeignKey('Screen',on_delete=models.CASCADE)
    purchased_seats = models.PositiveSmallIntegerField(default=0)
    on_sale = models.BooleanField(default=0)

# the primary key could be a unique, scanable qr/barcode
class Ticket(models.Model):
    # PROTECT avoid: customer paid for a ticket, now the show is cancelled
    movie = models.ForeignKey('Movie',on_delete=models.PROTECT)
