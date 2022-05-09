import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StudyMushroomsServer.settings")
django.setup()

from StudyMushroomsServer.users.models import Mushroom

class MushroomsManager:
    def reset_mushrooms(self):
        Mushroom.objects.all().delete()

    def save_new_mushroom(self, name, classname, picture_link, description, type):
        model = Mushroom()
        model.name = name
        model.classname = classname
        model.picture_link = picture_link
        model.description = description
        model.type = type
        model.save()