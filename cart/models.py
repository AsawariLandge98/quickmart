from django.db import models

class Cart(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=100, null=True, blank=True)
    coupon = models.ForeignKey('store.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"Cart - {self.user or self.session_key}"
    def get_subtotal(self):
        return sum(item.get_total() for item in self.items.all())
    def get_delivery_fee(self):
        return 0 if self.get_subtotal() >= 199 else 29
    def get_discount(self):
        if not self.coupon: return 0
        sub = self.get_subtotal()
        if self.coupon.discount_type == 'percentage':
            d = sub * self.coupon.discount_value / 100
            if self.coupon.max_discount: d = min(d, self.coupon.max_discount)
        else: d = self.coupon.discount_value
        return d
    def get_total(self):
        return self.get_subtotal() + self.get_delivery_fee() - self.get_discount()
    def get_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('store.ProductVariant', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    saved_for_later = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.variant.product.name} x{self.quantity}"
    def get_total(self): return self.variant.price * self.quantity
    class Meta: unique_together = [('cart','variant')]
