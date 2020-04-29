from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import *


# Register your models here.
@admin.register(MushroomPlace)
class PlaceAdmin(OSMGeoAdmin):
    list_display = ('mushroom', 'location')


@admin.register(Mushroom)
class MushroomAdmin(OSMGeoAdmin):
    list_display = ('id', 'name')


@admin.register(User)
class UserAdmin(OSMGeoAdmin):
    list_display = ('username', 'email')


@admin.register(Note)
class NoteAdmin(OSMGeoAdmin):
    list_display = ('user', 'date', 'content')
