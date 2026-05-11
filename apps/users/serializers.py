from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserNotificationPreference, UserActivityLog


class PetsoTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend the default JWT login response with user_id, email, name, and role."""

    def validate(self, attrs):
        data = super().validate(attrs)

        # Block login if email not confirmed
        if not self.user.is_email_verified:
            raise PermissionDenied(
                "Please verify your email before logging in."
            )

        data["user_id"] = self.user.pk
        data["email"] = self.user.email
        data["name"] = self.user.name
        data["role"] = self.user.role
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number', 'role', 'is_verified', 'date_joined')
        read_only_fields = ('id', 'is_verified', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'phone_number', 'role', 'is_verified')
        read_only_fields = ('is_verified',)

    def create(self, validated_data):
        with transaction.atomic():
            return User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                name=validated_data.get('name', ''),
                phone_number=validated_data.get('phone_number', ''),
                role=validated_data.get('role', 'farmer'),
                is_verified=False,
                is_email_verified=False,
            )

class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreference
        fields = '__all__'

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        fields = '__all__'
