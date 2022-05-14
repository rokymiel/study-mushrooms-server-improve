from django.contrib.gis.db import models


# Create your models here.
class Note(models.Model):
    user = models.ForeignKey('user_auth.User', on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()
    content = models.TextField()
    title = models.TextField(default='')

    class Meta:
        ordering = ['date']


class Mushroom(models.Model):
    classname = models.CharField(max_length=100, blank=True, default='')
    name = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    picture_link = models.CharField(max_length=100)
    type = models.CharField(max_length=10, default='')

    class Meta:
        ordering = ['id']


class MushroomPlace(models.Model):
    date = models.DateTimeField()
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    image = models.TextField(default='')

    class Meta:
        ordering = ['date']
