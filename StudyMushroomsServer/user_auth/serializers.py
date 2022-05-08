from rest_framework import serializers
from rest_framework.fields import empty

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'email')

    def validate(self, data):
        if data['email'] is None or data['username'] is None:
            raise serializers.ValidationError("Email and username must be not empty")

        return data
