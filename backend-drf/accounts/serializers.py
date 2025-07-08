from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def create(self, validated_data):
      # User.objects.create -> save the password in a plain text
      # User.objects.create_user -> save the password in a hashed format
      user = User.objects.create_user(
          username=validated_data['username'],
          email=validated_data['email'],
          password=validated_data['password']
      )
      # Alternatively, you can use the following line to create the user:
      # user = User.objects.create_user(**validated_data)
      return user