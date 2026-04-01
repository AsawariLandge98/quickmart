from django.db import models
import uuid

class Payment(models.Model):
    GATEWAY_CHOICES = [('razorpay','Razorpay'),('stripe','Stripe'),('cod','COD')]
    METHOD_CHOICES = [('upi','UPI'),('card','Card'),('netbanking','Netbanking'),('cod','COD'),('wallet','Wallet')]
    STATUS_CHOICES = [('pending','Pending'),('captured','Captured'),('failed','Failed'),('refunded','Refunded')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='payments')
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES, default='razorpay')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='upi')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default='INR')
    gateway_order_id = models.CharField(max_length=200, blank=True)
    gateway_payment_id = models.CharField(max_length=200, blank=True)
    gateway_signature = models.CharField(max_length=500, blank=True)
    refund_id = models.CharField(max_length=200, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Payment {self.id} - {self.status}"
    class Meta: ordering = ['-created_at']
