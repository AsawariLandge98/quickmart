from django.contrib import admin
from .models import Category, Brand, Product, ProductVariant, Review, Banner, Coupon, Wishlist

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category','brand','min_price','total_sold','average_rating','is_active','is_featured']
    list_filter = ['category','brand','is_active','is_featured','is_flash_sale']
    search_fields = ['name','sku']
    prepopulated_fields = {'slug':('name',)}
    inlines = [ProductVariantInline]
    list_editable = ['is_active','is_featured']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','slug','sort_order','is_active']
    prepopulated_fields = {'slug':('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name','is_active']
    prepopulated_fields = {'slug':('name',)}

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title','sort_order','is_active']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code','discount_type','discount_value','usage_count','is_active']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product','user','rating','created_at']
    list_filter = ['rating']
