from django.shortcuts import render
from rest_framework.views import APIView
from .models import User
from rest_framework import generics, status
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny 

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegistrationApiView(APIView):
    permission_classes = [AllowAny]  # Разрешаем доступ без аутентификации
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = Token.objects.create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthenticationApiView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'message': 'Authentication successful',
                'token': token.key,
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

from .serializers import UserProfileSerializer  # Импортируем новый сериализатор

# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from .serializers import UserProfileSerializer

class UserProfileAPIView(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
    
# views.py
from rest_framework.parsers import MultiPartParser
import uuid
from datetime import datetime

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Инициализируем Supabase клиент
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_BUCKET = 'user-avatars'

# Проверяем наличие обязательных переменных
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class AvatarUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def patch(self, request):
        user = request.user
        avatar_file = request.FILES.get('avatar')
        
        if not avatar_file:
            return Response({'error': 'No avatar file provided'}, status=400)

        try:
            file_ext = avatar_file.name.split('.')[-1].lower()
            filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = f"avatars/{filename}"

            # Загружаем в Supabase
            res = supabase.storage.from_(SUPABASE_BUCKET).upload(
                file_path,
                avatar_file.read(),
                file_options={"content-type": avatar_file.content_type}
            )

            if res.get('error'):
                return Response({'error': res['error']['message']}, status=500)

            avatar_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"

            # Убедись, что avatar_url есть в модели User
            user.avatar_url = avatar_url
            user.save()

            return Response(
                UserProfileSerializer(user, context={'request': request}).data,
                status=200
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)