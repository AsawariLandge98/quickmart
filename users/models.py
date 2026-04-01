from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid, random, string

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_admin', True)
        return self.create_user(email, password, **extra)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    full_name = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    reward_coins = models.IntegerField(default=100)
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    def __str__(self): return self.email
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = ''.join(random.choices(string.ascii_uppercase+string.digits, k=8))
        super().save(*args, **kwargs)
    @property
    def first_name(self): return self.full_name.split()[0] if self.full_name else ''

class Address(models.Model):
    LABEL_CHOICES = [('home','Home'),('work','Work'),('other','Other')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=10, choices=LABEL_CHOICES, default='home')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address_line1 = models.TextField()
    address_line2 = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.label} - {self.city}"
    class Meta:
        ordering = ['-is_default','-created_at']
        verbose_name_plural = 'Addresses'
