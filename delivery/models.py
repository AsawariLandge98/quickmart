from django.db import models

class DeliveryPartner(models.Model):
    STATUS_CHOICES = [('available','Available'),('on_delivery','On Delivery'),('offline','Offline'),('break','Break')]
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50, default='Bike')
    vehicle_number = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    current_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    total_deliveries = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user.full_name} - {self.status}"

class DeliveryTracking(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='tracking')
    partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True)
    pickup_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_minutes = models.IntegerField(default=10)
    def __str__(self): return f"Tracking for {self.order.order_number}"
