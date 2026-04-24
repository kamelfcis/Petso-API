from rest_framework import serializers
from .models import User, OTP, UserNotificationPreference, UserActivityLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number', 'role', 'is_verified', 'date_joined')
        read_only_fields = ('id', 'is_verified', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'phone_number', 'role')

    def create(self, validated_data):
        from django.utils import timezone
        import random
        from datetime import timedelta
        from .tasks import send_verification_email_task

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', 'farmer')
        )

        # Generate a 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(
            user=user,
            code=otp_code,
            purpose='verification',
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        # Dispatch background task to send the email via Celery
        try:
            send_verification_email_task.delay(user.email, otp_code)
        except Exception as e:
            pass # Logs will catch task connection errors if redis is down

        return user

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'

class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreference
        fields = '__all__'

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        fields = '__all__'
