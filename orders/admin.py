from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','user','status','payment_method','total_amount','placed_at']
    list_filter = ['status','payment_method']
    search_fields = ['order_number','user__email']
    inlines = [OrderItemInline]
