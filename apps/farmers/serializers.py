from rest_framework import serializers
from .models import FarmerProfile, PoultryFlock
from apps.users.serializers import UserSerializer

class FarmerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = FarmerProfile
        fields = '__all__'

class PoultryFlockSerializer(serializers.ModelSerializer):
    """`farmer` is optional for farmers: the view sets it from the JWT user."""

    class Meta:
        model = PoultryFlock
        fields = "__all__"
        extra_kwargs = {
            "farmer": {"required": False, "allow_null": True},
        }
