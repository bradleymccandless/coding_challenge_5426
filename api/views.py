import datetime
from django.http import JsonResponse
from api.models import Screen,Movie,Ticket
from json import loads

def screens(request):
    if request.method == 'GET':
        # I really wanted to use an off-the-shelf serializer here
        # but none can reuse primary keys as json indices easily.
        # after we remove it from the object since it's redundant
        data = {}
        for screen_object in Screen.objects.values():
            data[screen_object['id']] = screen_object
            movie_objects = Movie.objects.filter(screen=screen_object['id']).values()
            data[screen_object['id']]['movies'] = {}
            for movie_object in movie_objects:
                data[screen_object['id']]['movies'][movie_object['id']] = movie_object
                for e in ['id', 'screen_id']:
                    movie_object.pop(e)
            data[screen_object['id']].pop('id')
        return JsonResponse(data)
    elif request.method == 'POST':
        data = loads(request.body)
        if 'seats' not in data:
            return JsonResponse({'message': 'Screen API requires JSON with a \'seats\' index'}, status=400)
        try: 
            if data['seats'] < 1 or data['seats'] > 996:
                return JsonResponse({'message': 'Screen API requires JSON index \'seats\' to be an interger from 1 to 996'}, status=400)
        except:
            return JsonResponse({'message': 'Screen API requires JSON index \'seats\' to be an interger.'}, status=400)
        screen_object = Screen.objects.create(seats=data['seats'])
        return JsonResponse({'message': 'Screening room '+str(screen_object.id)+' added.'})
    else:
        return JsonResponse({'message': 'Screen API is GET or POST.'}, status=400)

def movies(request):
    if request.method == 'GET':
        # again, custom mini-serializer. one level deep this time.
        data = {}
        for object in Movie.objects.values():
            data[object['id']] = object 
            data[object['id']].pop('id')
        return JsonResponse(data)
    elif request.method == 'POST':
        data = loads(request.body)
        if 'screen' not in data:
            return JsonResponse({'message': 'Movie API requires JSON with a \'screen\' index'}, status=400)
        if data['screen'] not in list(Screen.objects.values_list('id', flat=True)):
            return JsonResponse({'message': 'Screen '+str(data['screen'])+' does not exist.'}, status=400)
        if 'showtime' not in data:
            data['showtime'] = datetime.datetime.now().time().replace(second=0, microsecond=0)
        else:
            try:
                datetime.datetime.strptime(data['showtime'], '%H:%M')
            except:
                return JsonResponse({'message': 'Showtime must be HH:MM.'}, status=400)
        movie_object = Movie.objects.create(screen=Screen.objects.get(id=data['screen']),showtime=data['showtime'])
        return JsonResponse({'message': 'Movie '+str(movie_object.id)+' added.'})
    else:
        return JsonResponse({'message': 'Movie API is GET or POST.'}, status=400)

def tickets(request):
    if request.method not in  ['PUT', 'POST']:
        return JsonResponse({'message': 'Ticket API is PUT or POST.'}, status=400)
    data = loads(request.body)
    if 'movie' in data:
        if not isinstance(data['movie'], int):
            return JsonResponse({'message': 'Ticnet API requires \'movie\' index to be an integer.'}, status=400)
        try:
            movie_object = Movie.objects.get(id=data['movie'])
        except:
            return JsonResponse({'message': 'Movie '+str(data['movie'])+' does not exist.'}, status=400)
        screen_object = Screen.objects.get(id=movie_object.screen_id)
        if screen_object.seats <= movie_object.purchased_seats:
            movie_object.on_sale = False
            movie_object.save()
    else:
        return JsonResponse({'message': 'Ticket API requires a \'movie\' index.'}, status=400)
    if request.method == 'PUT':
        # there has to be at least one ticket avaliable for the show to be on sale
        if movie_object.purchased_seats < screen_object.seats:
            movie_object.on_sale = True
            movie_object.save()
            return JsonResponse({'message': 'Movie '+str(data['movie'])+' is now on sale.'})
        else:
            return JsonResponse({'message': 'Movie '+str(data['movie'])+' is sold out.'}, status=400)
    elif request.method == 'POST':
        if (movie_object.on_sale == False):
            return JsonResponse({'message': 'Movie '+str(data['movie'])+' is not on sale.'}, status=400)
        if 'amount' not in data:
            data['amount'] = 1
        try:
            if data['amount'] < 1:
                return JsonResponse({'message': 'Amount of tickets must be 1 or more.'}, status=400) 
        except:
            return JsonResponse({'message': 'Ticket amount must be an integer.'}, status=400)
        if data['amount'] <= (screen_object.seats - movie_object.purchased_seats):
            movie_object.purchased_seats += data['amount']
            movie_object.save()
            ticket_ids = []
            # we could use bulk_create here to go fast
            # but only postgres will return a list of ids
            for i in range(0, data['amount']):
                ticket_object = Ticket(movie=movie_object)
                ticket_object.save()
                ticket_ids.append(ticket_object.id)
            return JsonResponse({'ticket_ids': ticket_ids})
        else: return JsonResponse({'message': 'Movie '+str(data['movie'])+' does not have enough seats.'}, status=400)
