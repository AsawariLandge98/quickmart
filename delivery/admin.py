from django.contrib import admin
from .models import DeliveryPartner, DeliveryTracking
@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ['user','vehicle_type','status','total_deliveries']
