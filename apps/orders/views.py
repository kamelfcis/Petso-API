from decimal import Decimal
import uuid

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.ecommerce.models import Cart, CartItem
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderSerializer, OrderItemSerializer, OrderStatusHistorySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items', 'items__product').all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'admin':
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        # Pull items from the user's cart
        cart = Cart.objects.filter(user=user).first()
        cart_items = list(CartItem.objects.filter(cart=cart).select_related('product')) if cart else []

        if not cart_items:
            raise ValidationError(
                {"cart": "Your cart is empty. Add products before placing an order."}
            )

        # Calculate total from cart
        total = sum(
            Decimal(str(item.unit_price)) * item.quantity for item in cart_items
        )

        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = serializer.save(
            user=user,
            order_number=order_number,
            total=total,
        )

        # Create OrderItems from cart
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=Decimal(str(item.unit_price)) * item.quantity,
            )

        # Clear the cart after order is placed
        CartItem.objects.filter(cart=cart).delete()

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = Order.objects.count()
        Order.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)

class OrderStatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderStatusHistory.objects.all()
    serializer_class = OrderStatusHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)
