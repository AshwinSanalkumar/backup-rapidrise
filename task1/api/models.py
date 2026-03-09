from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class User(AbstractUser):
    class Meta:
        db_table = "Accounts"

#PRODUCT MODELS
def product_image_path(instance, filename):
    return f'user_{instance.owner.id}/images/{filename}'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=product_image_path, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Products"

    def __str__(self):
        return self.name
    
#FIlE UPLOAD MODEL
def file_storage_path(instance, filename):
    return f'user_{instance.owner.id}/files/{filename}'

class UserFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.FileField(upload_to=file_storage_path)
    file_size_bytes = models.BigIntegerField()
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "Files"

#SHARED LINK MODEL
class SharedLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    file = models.ForeignKey(UserFile, on_delete=models.CASCADE, related_name='shares')
    is_accessed = models.BooleanField(default=False)
    expires_at = models.DateTimeField() 
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_expired(self):
        """Simple, direct security check."""
        return timezone.now() > self.expires_at
    
    class Meta:
        db_table = "SharedLink"