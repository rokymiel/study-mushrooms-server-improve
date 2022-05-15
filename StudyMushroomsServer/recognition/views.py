import base64

from PIL import Image
from django.core.files.base import ContentFile
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from StudyMushroomsServer.logger import base_logger
from recognition.inference import recognize
from .serializers import *
from ..base_api.models import Mushroom

logger = base_logger.getChild('recognition')


class RecognizeView(ListModelMixin, GenericAPIView):
    serializer_class = RecognizeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = ContentFile(base64.b64decode(request.data.get('image')))
        image = Image.open(file.open())

        mushrooms = Mushroom.objects.all()

        def create_model(probability, classname):
            return RecognizeModel(probability=probability,
                                  mushroom=mushrooms.filter(classname=classname)[0])

        res = recognize(image, create_model)

        res = sorted(res, key=lambda x: -x.probability)
        ser = self.get_serializer(res, many=True)
        print(ser)
        return Response(data=ser.data, status=status.HTTP_200_OK)
