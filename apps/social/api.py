from rest_framework import serializers, viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from petso_project.image_utils import base64_to_content_file, download_url_to_content_file

from .models import Post, Comment, PostLike


def _http_url_from_initial_image_url(initial_data):
    """POST bodies often use legacy key `image_url` for a remote picture URL."""
    if initial_data is None:
        return None
    if hasattr(initial_data, "get"):
        raw = initial_data.get("image_url")
    else:
        return None
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
    image_base64 = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Optional fallback when multipart file upload is unavailable (data URL or raw base64). Prefer field `image` with multipart/form-data.",
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "content",
            "image",
            "remote_image_url",
            "image_base64",
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
        b64 = attrs.get("image_base64")
        if isinstance(b64, str):
            b64 = b64.strip() or None
            attrs["image_base64"] = b64

        remote = attrs.get("remote_image_url")
        if isinstance(remote, str):
            remote = remote.strip() or None
            attrs["remote_image_url"] = remote
        if not remote:
            legacy = _http_url_from_initial_image_url(getattr(self, "initial_data", None))
            if legacy:
                attrs["remote_image_url"] = legacy
                remote = legacy

        n = sum(1 for x in (image, b64, remote) if x)
        if n > 1:
            raise ValidationError(
                "Use only one image source: file field `image`, `image_base64`, "
                "or `remote_image_url` / https `image_url`."
            )
        return attrs

    def create(self, validated_data):
        remote = validated_data.pop("remote_image_url", None)
        if isinstance(remote, str):
            remote = remote.strip() or None
        b64 = validated_data.pop("image_base64", None)
        if isinstance(b64, str):
            b64 = b64.strip() or None

        if remote:
            validated_data["image"] = download_url_to_content_file(remote)
            validated_data["image_url"] = remote
        elif b64:
            validated_data["image"] = base64_to_content_file(b64)
            validated_data["image_url"] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remote = validated_data.pop("remote_image_url", None)
        if isinstance(remote, str):
            remote = remote.strip() or None
        b64 = validated_data.pop("image_base64", None)
        if isinstance(b64, str):
            b64 = b64.strip() or None

        if remote:
            validated_data["image"] = download_url_to_content_file(remote)
            validated_data["image_url"] = remote
        elif b64:
            validated_data["image"] = base64_to_content_file(b64)
            validated_data["image_url"] = None
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
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @staticmethod
    def _write_request_data(request):
        """
        Prefer Django's parsed POST+FILES when any file was uploaded so the
        serializer sees the same keys as a Django form. Accessing POST first
        ensures multipart bodies are fully parsed on some servers (ASGI/nginx).
        """
        method = getattr(request, "method", "") or ""
        if method in ("POST", "PUT", "PATCH"):
            try:
                _ = request.POST  # noqa: F841  # triggers multipart parse + FILES
            except Exception:
                pass
        if request.FILES:
            data = request.POST.copy()
            for key, filelist in request.FILES.lists():
                data.setlist(key, filelist)
            return data
        return request.data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self._write_request_data(request))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=self._write_request_data(request), partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def _file_image_from_request(self):
        f = self.request.FILES.get("image")
        if f is None:
            return None
        size = getattr(f, "size", None)
        if size is not None and size <= 0:
            return None
        return f

    def perform_create(self, serializer):
        """
        If multipart dropped `image` from validated_data (proxy/parser quirks),
        attach the raw uploaded file from request.FILES when present.
        """
        vd = serializer.validated_data
        if vd.get("remote_image_url") or vd.get("image_base64"):
            serializer.save(user=self.request.user)
            return
        raw = self._file_image_from_request()
        if raw is not None:
            serializer.save(user=self.request.user, image=raw)
            return
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        vd = serializer.validated_data
        if vd.get("remote_image_url") or vd.get("image_base64"):
            serializer.save()
            return
        raw = self._file_image_from_request()
        if raw is not None:
            serializer.save(image=raw)
            return
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
