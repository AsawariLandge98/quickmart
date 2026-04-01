from django import forms
from .models import Product, ProductVariant

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','category','brand','description','short_description','sku','image','image_url','is_active','is_featured','is_flash_sale']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-input'}),
            'description': forms.Textarea(attrs={'class':'form-input','rows':4}),
        }
