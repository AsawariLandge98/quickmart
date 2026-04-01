from django.contrib import admin
from .models import Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id','order','gateway','method','status','amount','created_at']
    list_filter = ['gateway','method','status']
