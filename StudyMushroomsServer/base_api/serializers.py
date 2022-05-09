from rest_framework import serializers
from rest_framework.fields import empty

from .models import *


class MushroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mushroom
        fields = ('pk', 'name', 'type', 'picture_link', 'description')


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MushroomPlace
        fields = ('pk', 'date', 'longitude', 'latitude', 'image')


class RecognizeSerializer(serializers.ModelSerializer):
    mushroom = MushroomSerializer(many=False, required=True)

    class Meta:
        model = RecognizeModel
        fields = ('mushroom', 'probability')


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('pk', 'date', 'user', 'content', 'title')
