import mimetypes
import uuid
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from rest_framework import serializers, viewsets, permissions
from rest_framework.exceptions import ValidationError

from .models import Post, Comment, PostLike

# Max download size for remote_image_url (bytes)
MAX_POST_IMAGE_BYTES = 5 * 1024 * 1024


def _unsafe_image_host(hostname: str) -> bool:
    if not hostname:
        return True
    h = hostname.lower()
    if h in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return True
    if h.endswith(".local") or h.endswith(".internal"):
        return True
    if h.startswith("192.168.") or h.startswith("10.") or h.startswith("172.16."):
        return True
    if h.startswith("172.17.") or h.startswith("172.18."):
        return True
    if h.startswith("172.19.") or h.startswith("172.2") or h.startswith("172.30.") or h.startswith("172.31."):
        return True
    return False


def download_url_to_content_file(url: str) -> ContentFile:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValidationError("Image URL must use http or https.")
    if _unsafe_image_host(parsed.hostname or ""):
        raise ValidationError("Image URL host is not allowed.")

    req = Request(url.strip(), headers={"User-Agent": "Petso-Server/1.0"})
    with urlopen(req, timeout=25) as resp:
        ctype = resp.headers.get("Content-Type", "application/octet-stream")
        ctype = ctype.split(";")[0].strip()
        data = resp.read(MAX_POST_IMAGE_BYTES + 1)

    if len(data) > MAX_POST_IMAGE_BYTES:
        raise ValidationError("Image exceeds maximum size (5 MB).")

    ext = mimetypes.guess_extension(ctype) or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
        ext = ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    return ContentFile(data, name=name)


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField(read_only=True)
    # Full URL for clients (uploaded file or legacy external link)
    image_url = serializers.SerializerMethodField(read_only=True)
    # POST JSON: fetch this URL and store file in `image`
    remote_image_url = serializers.URLField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Optional. HTTP(S) URL to download and store as the post image.",
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "content",
            "image",
            "remote_image_url",
            "image_url",
            "created_at",
            "likes_count",
        )
        read_only_fields = ("image_url",)
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

    def get_likes_count(self, obj):
        return obj.likes.count()

    def validate(self, attrs):
        image = attrs.get("image")
        remote = attrs.get("remote_image_url")
        if image and remote:
            raise ValidationError("Provide either an uploaded image file or remote_image_url, not both.")
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


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
