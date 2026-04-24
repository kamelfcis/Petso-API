from rest_framework import serializers
from .models import VetProfile, VetReview
from apps.users.serializers import UserSerializer

class VetProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = VetProfile
        fields = '__all__'

class VetReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetReview
        fields = '__all__'
