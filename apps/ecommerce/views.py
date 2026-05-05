from django.db.models import Max
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import Category, Product, ProductImage, Cart, CartItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    CartSerializer,
    CartItemSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category", "company").prefetch_related("images", "reviews")
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_fields = ["category", "company", "requires_prescription", "is_active"]
    search_fields = ["name", "description", "sku"]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @staticmethod
    def _write_request_data(request):
        """Same multipart merge as social posts so `image` file reaches the serializer."""
        method = getattr(request, "method", "") or ""
        if method in ("POST", "PUT", "PATCH"):
            try:
                _ = request.POST  # noqa: F841
            except Exception:
                pass
        if request.FILES:
            data = request.POST.copy()
            for key, filelist in request.FILES.lists():
                data.setlist(key, filelist)
            return data
        return request.data

    @staticmethod
    def _primary_product_image_file(request):
        f = request.FILES.get("image")
        if f is None:
            return None
        if getattr(f, "size", None) is not None and f.size <= 0:
            return None
        return f

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self._write_request_data(request))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        product = Product.objects.prefetch_related("images", "reviews").get(pk=serializer.instance.pk)
        out = self.get_serializer(product)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=self._write_request_data(request), partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        product = Product.objects.prefetch_related("images", "reviews").get(pk=serializer.instance.pk)
        return Response(self.get_serializer(product).data)

    def _attach_uploaded_product_image(self, product):
        raw = self._primary_product_image_file(self.request)
        if raw is None:
            return
        mx = product.images.aggregate(Max("position"))["position__max"]
        next_pos = (mx if mx is not None else -1) + 1
        ProductImage.objects.create(
            product=product,
            image=raw,
            position=next_pos,
            image_url=None,
        )

    def perform_create(self, serializer):
        product = serializer.save()
        self._attach_uploaded_product_image(product)

    def perform_update(self, serializer):
        product = serializer.save()
        self._attach_uploaded_product_image(product)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list" and "is_active" not in self.request.query_params:
            qs = qs.filter(is_active=True)
        return qs


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.select_related("product").all().order_by("product", "position", "id")
    serializer_class = ProductImageSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_fields = ["product"]

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product,
                defaults={'unit_price': product.unit_price, 'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
