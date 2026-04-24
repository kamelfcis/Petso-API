from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderSerializer, OrderItemSerializer, OrderStatusHistorySerializer
import uuid

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        serializer.save(user=self.request.user, order_number=order_number)

class OrderStatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderStatusHistory.objects.all()
    serializer_class = OrderStatusHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)
