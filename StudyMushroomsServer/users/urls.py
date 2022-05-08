from django.contrib import admin
from django.urls import path, include
from .views import *

from StudyMushroomsServer.user_auth.requests import login, create_auth

urlpatterns = [
    path('login', login),
    path('register', create_auth),
    path('user_info', UserView.as_view()),
    path('places', PlaceView.as_view()),
    path('notes', NoteView.as_view()),
    path('recognize', RecognizeView.as_view()),
    path('mushrooms', MushroomView.as_view())
]
