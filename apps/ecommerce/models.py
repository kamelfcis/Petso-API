from django.db import models
from django.conf import settings
from apps.companies.models import Company
from django.utils.text import slugify

_SLUG_MAX_LEN = 50  # SlugField default max_length


def _unique_slug_for(model_cls, source: str, *, exclude_pk=None) -> str:
    """Build a slug from `source` (typically name) that does not collide with existing rows."""
    base = slugify(source) or "item"
    base = base[:_SLUG_MAX_LEN]
    slug = base
    qs = model_cls.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    n = 1
    while qs.filter(slug=slug).exists():
        n += 1
        suffix = f"-{n}"
        trunc = max(1, _SLUG_MAX_LEN - len(suffix))
        slug = f"{base[:trunc]}{suffix}"
    return slug


class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name", "id")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug_for(Category, self.name, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    requires_prescription = models.BooleanField(default=False)
    expiration_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "id")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug_for(Product, self.name, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="ecommerce/products/", blank=True, null=True)
    # Original remote URL (optional) or legacy link when no file is stored
    image_url = models.URLField(blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField()
    title = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    discount_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses = models.IntegerField(default=100)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) # Snapshot
    created_at = models.DateTimeField(auto_now_add=True)

class CartDiscount(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_discounts')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    applied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
