from django.db import models
from django.conf import settings
from apps.ecommerce.models import Product, Discount
from apps.companies.models import Company

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.TextField()
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50) # e.g., 'Wallet', 'Card'
    prescription_id = models.IntegerField(blank=True, null=True) # Will link to medical prescription later
    delivery_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

class OrderDiscount(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_discounts')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    applied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
