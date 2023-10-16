from django.contrib.auth.hashers import make_password
from django.forms import ValidationError
from rest_framework import status
from rest_framework import serializers

from authentication.models import User

class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=40,allow_blank=False)
    display_name = serializers.CharField(max_length=40,allow_blank=False)
    email = serializers.EmailField(max_length=60,allow_blank=False)
    password=serializers.CharField(allow_blank=False,write_only=True)

    class Meta: 
        model = User
        fields = ['id', 'username', 'display_name', 'email', 'password'] 

    
    def validate(self, attrs):
        email = User.objects.filter(email=attrs.get('email')).exists()
        if email:
            raise ValidationError(detail="User with email exists",code=status.HTTP_403_FORBIDDEN)

        username = User.objects.filter(username=attrs.get('username')).exists()
        if username:
            raise ValidationError(detail="User with username exists",code=status.HTTP_403_FORBIDDEN)

        return super().validate(attrs)

    def create(self,validated_data):
        new_user = User(**validated_data)
        new_user.password = make_password(new_user.password)

        new_user.save()

        return new_user
    