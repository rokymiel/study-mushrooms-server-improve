from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from StudyMushroomsServer.logger import base_logger
from common.constants import classnames
from recognition.validate import mushrooms_recognition_model
from .serializers import *
from PIL import Image
import torch
import torchvision
import base64
from ..base_api.models import Mushroom

logger = base_logger.getChild('recognition')


class RecognizeView(ListModelMixin, GenericAPIView):
    serializer_class = RecognizeSerializer
    pagination_class = LimitOffsetPagination

    def post(self, request, *args, **kwargs):
        file = ContentFile(base64.b64decode(request.data.get('image')))
        image = Image.open(file.open())
        preprocess = torchvision.transforms.Compose([
            torchvision.transforms.Resize(256),
            torchvision.transforms.CenterCrop(224),
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        tensor = preprocess(image)
        batch = tensor.unsqueeze(0)

        if torch.cuda.is_available():
            batch = batch.to('cuda')
            mushrooms_recognition_model.to('cuda')
        with torch.no_grad():
            output = mushrooms_recognition_model(batch)

        probs = torch.nn.functional.softmax(output[0], dim=0)
        res = []
        mushrooms = Mushroom.objects.all()
        for i in range(len(classnames)):
            if probs[i].item().__float__() > 0.01:
                res.append(RecognizeModel(probability=probs[i].item().__float__(),
                                          mushroom=mushrooms.filter(classname=classnames[i])[0]))
        res = sorted(res, key=lambda x: -x.probability)
        ser = self.get_serializer(res, many=True)
        print(ser)
        return Response(data=ser.data, status=status.HTTP_200_OK)