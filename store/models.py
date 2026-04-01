from django.db import models
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    icon = models.CharField(max_length=10, default='🛒')
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    class Meta: ordering = ['sort_order','name']; verbose_name_plural='Categories'

class Brand(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=600)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    image2 = models.ImageField(upload_to='products/', null=True, blank=True)
    image3 = models.ImageField(upload_to='products/', null=True, blank=True)
    image_url = models.URLField(blank=True, help_text="External image URL (use if no upload)")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma separated tags")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    total_reviews = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.name
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    @property
    def default_variant(self):
        return self.variants.filter(is_active=True).first()
    @property
    def min_price(self):
        v = self.default_variant
        return v.price if v else 0
    @property
    def display_image(self):
        if self.image: return self.image.url
        if self.image_url: return self.image_url
        return None
    class Meta: ordering = ['-created_at']

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.IntegerField(default=100)
    def __str__(self): return f"{self.product.name} - {self.name}"
    @property
    def discount_percentage(self):
        if self.mrp and self.mrp > self.price:
            return int(((self.mrp - self.price) / self.mrp) * 100)
        return 0
    @property
    def is_in_stock(self): return self.stock > 0

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    image = models.ImageField(upload_to='reviews/', null=True, blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.product.name} - {self.rating}★"
    class Meta: ordering = ['-created_at']

class Banner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='banners/', null=True, blank=True)
    image_url = models.URLField(blank=True)
    bg_color = models.CharField(max_length=50, default='linear-gradient(135deg,#1a1a2e,#16213e)')
    link_url = models.CharField(max_length=500, blank=True)
    button_text = models.CharField(max_length=100, default='Shop Now')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    emoji = models.CharField(max_length=10, blank=True)
    def __str__(self): return self.title
    class Meta: ordering = ['sort_order']

class Coupon(models.Model):
    TYPE_CHOICES = [('percentage','Percentage'),('flat','Flat')]
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300)
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    max_discount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    def __str__(self): return self.code

class Wishlist(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = [('user','product')]
