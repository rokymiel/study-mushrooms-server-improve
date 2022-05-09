from rest_framework import serializers
from .models import *


class MushroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mushroom
        fields = ('pk', 'name', 'type', 'picture_link', 'description')


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MushroomPlace
        fields = ('pk', 'date', 'longitude', 'latitude', 'image')


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('pk', 'date', 'user', 'content', 'title')
