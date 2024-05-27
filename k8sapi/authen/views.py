from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserSerializer

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response(token, status=status.HTTP_200_OK)
