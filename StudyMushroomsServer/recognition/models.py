from django.contrib.gis.db import models

# Create your models here.
class RecognizeModel(models.Model):
    mushroom = models.ForeignKey('base_api.Mushroom', on_delete=models.CASCADE, null=True)
    probability = models.FloatField()