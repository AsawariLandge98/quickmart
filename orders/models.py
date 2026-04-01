from django.db import models
import uuid, random, string

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),('confirmed','Confirmed'),('picking','Picking'),
        ('packed','Packed'),('dispatched','Dispatched'),('out_for_delivery','Out for Delivery'),
        ('delivered','Delivered'),('cancelled','Cancelled'),('refund_initiated','Refund Initiated'),
        ('refunded','Refunded'),
    ]
    PAYMENT_METHODS = [('upi','UPI'),('card','Card'),('netbanking','Netbanking'),
                       ('wallet','Wallet'),('cod','Cash on Delivery')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='orders')
    delivery_address = models.ForeignKey('users.Address', on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    payment_status = models.CharField(max_length=20, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = models.CharField(max_length=50, blank=True)
    coins_used = models.IntegerField(default=0)
    coins_earned = models.IntegerField(default=0)
    special_instructions = models.TextField(blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    razorpay_order_id = models.CharField(max_length=200, blank=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.order_number
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = 'QM' + ''.join(random.choices(string.digits, k=10))
        super().save(*args, **kwargs)
    @property
    def status_badge(self):
        colors = {
            'pending':'warning','confirmed':'info','picking':'info','packed':'info',
            'dispatched':'primary','out_for_delivery':'primary','delivered':'success',
            'cancelled':'danger','refund_initiated':'warning','refunded':'secondary'
        }
        return colors.get(self.status,'secondary')
    class Meta: ordering = ['-placed_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('store.ProductVariant', on_delete=models.PROTECT)
    product_name = models.CharField(max_length=500)
    variant_name = models.CharField(max_length=200)
    product_image = models.CharField(max_length=500, blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return f"{self.product_name} x{self.quantity}"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=30)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['created_at']
