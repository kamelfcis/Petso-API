from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview, Discount, Cart, CartItem, CartDiscount

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'created_at')
    search_fields = ('name',)
    list_filter = ('parent', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'category', 'unit_price', 'stock', 'is_active', 'requires_prescription', 'created_at')
    search_fields = ('name', 'sku', 'company__name')
    list_filter = ('category', 'company', 'is_active', 'requires_prescription', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__email', 'body')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'is_active', 'starts_at', 'ends_at')
    list_filter = ('discount_type', 'is_active', 'starts_at', 'ends_at')
    search_fields = ('code', 'description')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'unit_price', 'created_at')
