from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()  # Добавляем поле avatar_url

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'avatar_url']
        read_only_fields = ['id', 'date_joined']
    
    def get_avatar_url(self, obj):  # Имя метода должно совпадать с полем avatar_url
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None