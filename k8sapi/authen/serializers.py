
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            "username": representation["username"],
            "email": representation["email"],
            "message": "User created successfully"
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Must include "email" and "password"')

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        update_last_login(None, user)
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
