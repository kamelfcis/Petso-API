from rest_framework import serializers
from .models import VetProfile, VetReview
from apps.users.serializers import UserSerializer

class VetProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = VetProfile
        fields = '__all__'
        read_only_fields = ('is_admin_verified', 'user', 'id', 'created_at', 'updated_at', 'rating')

class VetRegistrationSerializer(serializers.Serializer):
    """Serializer for vet registration with license PDF upload."""
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    license_number = serializers.CharField(max_length=50)
    license_document = serializers.FileField(required=True)
    specialties = serializers.CharField(max_length=255)
    qualifications = serializers.CharField()
    clinic_address = serializers.CharField()
    years_of_experience = serializers.IntegerField(min_value=0)
    gps_lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    gps_long = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    def validate_license_document(self, file):
        # Validate file is PDF
        if not file.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("License document must be a PDF file.")
        return file

    def create(self, validated_data):
        from django.db import transaction
        from apps.users.models import User

        with transaction.atomic():
            # Create user
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                name=validated_data['name'],
                phone_number=validated_data.get('phone_number', ''),
                role='vet',
                is_verified=False,
                is_email_verified=False,
            )

            # Create vet profile (not admin verified initially)
            vet_profile = VetProfile.objects.create(
                user=user,
                license_number=validated_data['license_number'],
                license_document=validated_data['license_document'],
                specialties=validated_data['specialties'],
                qualifications=validated_data['qualifications'],
                clinic_address=validated_data['clinic_address'],
                years_of_experience=validated_data['years_of_experience'],
                gps_lat=validated_data.get('gps_lat'),
                gps_long=validated_data.get('gps_long'),
                is_admin_verified=False,
            )

            return vet_profile

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
