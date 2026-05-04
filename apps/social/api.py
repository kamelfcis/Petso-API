from rest_framework import serializers, viewsets, permissions
from rest_framework.exceptions import ValidationError

from petso_project.image_utils import download_url_to_content_file

from .models import Post, Comment, PostLike


def _http_url_from_initial_image_url(initial_data):
    """POST bodies often use legacy key `image_url` for a remote picture URL."""
    if not isinstance(initial_data, dict):
        return None
    raw = initial_data.get("image_url")
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s.lower().startswith(("http://", "https://")):
        return None
    return s


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
        if isinstance(remote, str):
            remote = remote.strip() or None
            attrs["remote_image_url"] = remote
        if not remote:
            legacy = _http_url_from_initial_image_url(getattr(self, "initial_data", None))
            if legacy:
                attrs["remote_image_url"] = legacy
                remote = legacy
        if image and remote:
            raise ValidationError("Provide either an uploaded image file or remote_image_url, not both.")
        return attrs

    def create(self, validated_data):
        remote = validated_data.pop("remote_image_url", None)
        if isinstance(remote, str):
            remote = remote.strip() or None
        if remote:
            validated_data["image"] = download_url_to_content_file(remote)
            validated_data["image_url"] = remote
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remote = validated_data.pop("remote_image_url", None)
        if isinstance(remote, str):
            remote = remote.strip() or None
        if remote:
            validated_data["image"] = download_url_to_content_file(remote)
            validated_data["image_url"] = remote
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
