from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductImageViewSet, CartViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-images', ProductImageViewSet, basename='product-image')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]
