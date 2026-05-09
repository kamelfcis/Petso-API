from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, OrderDiscount

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price', 'created_at')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'company',
            'shipping_address', 'status', 'total',
            'payment_method', 'prescription_id',
            'delivery_date', 'created_at', 'items',
        )
        read_only_fields = ('user', 'order_number', 'status', 'total')

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = '__all__'
