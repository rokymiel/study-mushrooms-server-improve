import uuid

from django.contrib.auth.models import PermissionsMixin

from StudyMushroomsServer.settings import MEDIA_ROOT, MEDIA_URL
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from django.utils.timezone import now
from StudyMushroomsServer.logger import base_logger
from .serializers import *
import base64

# Create your views here.
from StudyMushroomsServer.user_auth.models import User
from StudyMushroomsServer.user_auth.serializers import UserSerializer

logger = base_logger.getChild('base_api')


class PlaceView(PermissionsMixin, ListModelMixin, GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceSerializer
    pagination_class = LimitOffsetPagination
    queryset = MushroomPlace.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        logger.info("Received request for user's mushroom places")
        user = request.user
        print(user)
        queryset = user.mushroom_places.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        logger.info("Responding normally")
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        logger.info("Received request to add a mushroom place for the user")
        user = request.user
        place = MushroomPlace()
        place.date = now()
        imageb64 = base64.b64decode(request.data.get('image'))
        name = str(uuid.uuid4()) + '.jpg'
        print(name)
        with open(MEDIA_ROOT + 'images/' + name, 'wb') as f:
            place.image = MEDIA_URL + 'images/' + name
            f.write(imageb64)
            f.close()
        s = request.data.get('location')
        print(s)
        place.longitude = s['mPosition']['mStorage'][1]
        place.latitude = s['mPosition']['mStorage'][0]
        place.save()
        user.mushroom_places.add(place)
        user.save()
        return Response("Place at " + str(place.longitude) + " " + str(place.latitude) + "successfully added",
                        status.HTTP_200_OK)


class MushroomView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Mushroom.objects.all()
    serializer_class = MushroomSerializer
    pagination_class = LimitOffsetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        logger.info("Received request for user's mushroom places")
        queryset = Mushroom.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        logger.info("Responding normally")
        return Response(serializer.data)


class NoteView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = LimitOffsetPagination

    class Meta:
        model = Note
        fields = ('content', 'title', 'date', 'user')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        logger.info("Received request for user's mushroom places")
        user = request.user

        queryset = Note.objects.all().filter(user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        logger.info("Responding normally")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        logger.info('Received request to add a note')

        data = {
            'date': now(),
            'content': request.data.get('content'),
            'title': request.data.get('title'),
            'user': request.user.id
        }

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, *args, **kwargs):
        Note.objects.all().filter(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, *args, **kwargs):
        update_instance = Note.objects.get(pk=pk)

        # допустим, датой заметки будет дата ее последнего изменения
        data = {
            'date': now(),
            'content': request.data.get('content'),
            'title': request.data.get('title'),
            'user': request.user.id
        }

        serializer = self.get_serializer(instance=update_instance, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)