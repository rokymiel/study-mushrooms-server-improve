from rest_framework import serializers
from .models import *
from ..base_api.serializers import MushroomSerializer


class RecognizeSerializer(serializers.ModelSerializer):
    mushroom = MushroomSerializer(many=False, required=True)

    class Meta:
        model = RecognizeModel
        fields = ('mushroom', 'probability')