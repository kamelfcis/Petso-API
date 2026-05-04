from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
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
