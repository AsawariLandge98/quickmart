from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Address

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Create password','class':'form-input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm password','class':'form-input'}))
    class Meta:
        model = User
        fields = ['full_name','email','phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder':'Full name','class':'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder':'Email address','class':'form-input'}),
            'phone': forms.TextInput(attrs={'placeholder':'Phone number','class':'form-input'}),
        }
    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Passwords do not match')
        return cd
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit: user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email address','class':'form-input','autofocus':True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password','class':'form-input'}))

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['label','full_name','phone','address_line1','address_line2','city','state','pincode','landmark','is_default']
        widgets = {
            'label': forms.Select(attrs={'class':'form-input'}),
            'full_name': forms.TextInput(attrs={'placeholder':'Full name','class':'form-input'}),
            'phone': forms.TextInput(attrs={'placeholder':'Phone','class':'form-input'}),
            'address_line1': forms.TextInput(attrs={'placeholder':'Address line 1','class':'form-input'}),
            'address_line2': forms.TextInput(attrs={'placeholder':'Address line 2 (optional)','class':'form-input'}),
            'city': forms.TextInput(attrs={'placeholder':'City','class':'form-input'}),
            'state': forms.TextInput(attrs={'placeholder':'State','class':'form-input'}),
            'pincode': forms.TextInput(attrs={'placeholder':'Pincode','class':'form-input'}),
            'landmark': forms.TextInput(attrs={'placeholder':'Landmark (optional)','class':'form-input'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name','phone','profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class':'form-input'}),
            'phone': forms.TextInput(attrs={'class':'form-input'}),
        }
