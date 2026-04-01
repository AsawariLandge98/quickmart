from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email','full_name','phone','reward_coins','is_active','date_joined']
    list_filter = ['is_active','is_staff']
    search_fields = ['email','full_name','phone']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Personal', {'fields': ('full_name','phone','profile_image')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
        ('Rewards', {'fields': ('reward_coins','referral_code')}),
    )
    add_fieldsets = (
        (None, {'classes':('wide',),'fields':('email','full_name','password1','password2')}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user','label','city','state','pincode','is_default']
    list_filter = ['label','city']
