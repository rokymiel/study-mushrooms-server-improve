from rest_framework import serializers
from rest_framework.fields import empty

from .models import *


class MushroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mushroom
        fields = ('pk', 'name', 'type', 'picture_link', 'description')


class PlaceSerializer(serializers.ModelSerializer):
    mushroom = MushroomSerializer(many=False, required=False)

    class Meta:
        model = MushroomPlace
        fields = ('pk', 'location', 'mushroom', 'image')


class UserSerializer(serializers.ModelSerializer):
    mushroom_places = PlaceSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'mushroom_places', 'username', 'email')

    def validate(self, data):
        if data['email'] is None or data['username'] is None:
            raise serializers.ValidationError("Email and username must be not empty")

        return data


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('date', 'user', 'content')
