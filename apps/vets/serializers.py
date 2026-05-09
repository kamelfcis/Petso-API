from rest_framework import serializers
from .models import VetProfile, VetReview
from apps.users.serializers import UserSerializer

class VetProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = VetProfile
        fields = '__all__'

class VetReviewSerializer(serializers.ModelSerializer):
    vet_name = serializers.CharField(source="vet.user.name", read_only=True)
    farmer_name = serializers.CharField(source="farmer.user.name", read_only=True)

    class Meta:
        model = VetReview
        fields = (
            "id",
            "vet",
            "vet_name",
            "farmer",
            "farmer_name",
            "rating",
            "review_text",
            "created_at",
            "updated_at",
        )
