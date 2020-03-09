from django.urls import path

from . import views

urlpatterns = [
    path('screens', views.screens),
    path('movies', views.movies),
    path('tickets', views.tickets),
]
