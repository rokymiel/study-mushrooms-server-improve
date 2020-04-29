from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('add_place', add_place),
    path('login', login),
    path('register', create_auth),
    path('user_info', UserView.as_view()),
    path('places', PlaceView.as_view()),
    path('notes', NoteView.as_view()),
    # path('')
]
