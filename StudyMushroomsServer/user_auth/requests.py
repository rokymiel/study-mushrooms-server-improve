from django.contrib.auth import authenticate
from rest_framework import permissions
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from StudyMushroomsServer.logger import base_logger
from .serializers import *

logger = base_logger.getChild('auth')


class UserView(ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_auth(request):
    logger.info("Received request to register a user")
    serialized = UserSerializer(data=request.data)

    username = request.data.get('username')
    if User.objects.all().filter(username=username).exists():
        return Response({"error": "Duplicate username"},
                        status=status.HTTP_400_BAD_REQUEST)

    mail = request.data.get('email')
    if User.objects.all().filter(email=mail).exists():
        return Response({"error": "Duplicate email"},
                        status=status.HTTP_400_BAD_REQUEST)

    if serialized.is_valid():

        pswd = request.data.get('password')
        if len(pswd) < 8 or len(pswd) > 30 or not pswd.isalnum():
            logger.error("Invalid new password. Responding with 400")
            return Response({"error": "Invalid password"},
                            status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(
            email=request.data.get('email'),
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        logger.info("Registered successfully")
        token, _ = Token.objects.get_or_create(user=User.objects.get(username=username))
        logger.info("Logged in successfully. Returning a token. Responding normally")
        return Response({'token': token.key},
                        status=HTTP_200_OK)

    else:
        print(serialized.errors)
        logger.error("Failed to register. Responding with 400")
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    logger.info("Received request to login")
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or password is None:
        logger.error("No username or password. Responding with 400")
        return Response({'error': 'No username or password'},
                        status=HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        logger.error("Invalid credentials. Responding with 404")
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    logger.info("Logged in successfully. Returning a token. Responding normally")
    return Response({'token': token.key},
                    status=HTTP_200_OK)