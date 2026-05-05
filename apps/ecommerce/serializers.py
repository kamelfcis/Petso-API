from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from petso_project.image_utils import download_url_to_content_file

from .models import Category, Product, ProductImage, ProductReview, Discount, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    """GET: absolute `image_url`. POST: `image` file and/or `remote_image_url` (not both)."""

    image_url = serializers.SerializerMethodField(read_only=True)
    remote_image_url = serializers.URLField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Optional. Download and store as `image` on disk.",
    )

    class Meta:
        model = ProductImage
        fields = (
            "id",
            "product",
            "image",
            "remote_image_url",
            "image_url",
            "alt_text",
            "position",
            "created_at",
        )
        read_only_fields = ("id", "image_url", "created_at")
        extra_kwargs = {"image": {"required": False, "allow_null": True}}

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            path = obj.image.url
            if request:
                return request.build_absolute_uri(path)
            return path
        if obj.image_url:
            return str(obj.image_url)
        return None

    def validate(self, attrs):
        image = attrs.get("image")
        remote = attrs.get("remote_image_url")
        if image and remote:
            raise ValidationError("Provide either `image` file or remote_image_url, not both.")
        if not image and not remote:
            raise ValidationError("Provide an uploaded `image` file or `remote_image_url`.")
        return attrs

    def create(self, validated_data):
        remote = validated_data.pop("remote_image_url", None)
        if remote:
            validated_data["image"] = download_url_to_content_file(remote)
            validated_data["image_url"] = remote.strip()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remote = validated_data.pop("remote_image_url", None)
        if remote:
            validated_data["image"] = download_url_to_content_file(remote)
            validated_data["image_url"] = remote.strip()
        return super().update(instance, validated_data)


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    # Create/update: list of { remote_image_url?, alt_text?, position? } — same rules as ProductImage
    images_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text=(
            "Optional (JSON). Each item creates a ProductImage via remote_image_url download. "
            "For multipart, omit this and send form field `image` (File) on POST/PATCH /ecommerce/products/ "
            "same pattern as social posts."
        ),
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "company",
            "category",
            "sku",
            "name",
            "slug",
            "description",
            "unit_price",
            "currency",
            "stock",
            "is_active",
            "requires_prescription",
            "expiration_date",
            "created_at",
            "images",
            "reviews",
            "images_data",
        )
        read_only_fields = ("slug", "created_at")

    def create(self, validated_data):
        images_data = validated_data.pop("images_data", [])
        product = super().create(validated_data)
        for raw in images_data:
            ser = ProductImageSerializer(data=raw, context=self.context)
            ser.is_valid(raise_exception=True)
            ser.save(product=product)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images_data", None)
        product = super().update(instance, validated_data)
        if images_data is not None:
            instance.images.all().delete()
            for raw in images_data:
                ser = ProductImageSerializer(data=raw, context=self.context)
                ser.is_valid(raise_exception=True)
                ser.save(product=product)
        return product


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"
