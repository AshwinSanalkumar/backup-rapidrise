from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import Product, UserFile, SharedLink
from django.conf import settings
from datetime import timedelta
from django.urls import reverse


User = get_user_model()

# SERVICES FOR AUTHENTICATION
class AuthService:
    @staticmethod
    def register_user(validated_data):
        """
        api: api/register
        Service used to Create an User
        """
        return User.objects.create_user(
            username=validated_data['username'].lower().strip(),
            email=validated_data['email'].lower().strip(),
            password=validated_data['password'],
            first_name=validated_data['first_name'].strip().capitalize(),
            last_name=validated_data['last_name'].strip().capitalize()
        )
    @staticmethod
    def logout_user(refresh_token_str: str):
        """
        api : api/logout/
        Service used to Black list the token (logout).
        """
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
        except Exception as _e:
            raise ValidationError("Invalid or already blacklisted token.")
        
# SERVICES FRO PRODUCTS CRUD
class ProductService:
    
    @staticmethod
    def get_all_active(user):
        """
        api : api/products/
        Get all products that belong to user and not deleted
        """
        return Product.objects.filter(owner=user, is_deleted=False).order_by('-created_at')

    @staticmethod
    def create_product(user, data, image_file=None):
        """
        api : api/products/add/
        Add a Product
        """
        return Product.objects.create(
            owner=user,
            name=data.get('name'),
            description=data.get('description', ''),
            price=data.get('price'),
            stock_quantity=data.get('stock_quantity', 0),
            image=image_file
        )

    @staticmethod
    def update_product(product, data, image_file=None):
        """
        api : api/products/update/<product id>/
        Update a particular product
        """
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
        
        if image_file:
            product.image = image_file
            
        product.save()
        return product

    @staticmethod
    def soft_delete_product(product):
        """
        api : api/products/delete/<product id>/
        Delete a Particular product
        """
        product.is_deleted = True
        product.deleted_at = timezone.now()
        product.save()

# SERVICES FRO FILE UPLOAD DOWNLOAD
class FileStorageService:

    @staticmethod
    def process_and_store_file(user, file_obj):
        """
        api : api/files/upload/
        Upload the file
        """
        if file_obj.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE
            raise ValidationError(f"File exceeds {max_mb}MB limit.")
        mime_type = file_obj.content_type or 'application/octet-stream'
        ALLOWED_TYPES = [
            'image/jpeg', 'image/png', 'application/pdf', 
            'video/mp4', 'text/plain'
        ]

        if mime_type not in ALLOWED_TYPES:
            raise ValidationError(f"File type {mime_type} is not supported.")
        return UserFile.objects.create(
            owner=user,
            content=file_obj,
            filename=file_obj.name,
            file_size_bytes=file_obj.size,
            mime_type=mime_type
        )
    
    @staticmethod
    def create_shareable_data(file_obj, request, duration_minutes=5):
        """
        api: api/files/<file_id>/generate-link/
        Generate Secure Link for download
        """
        try:
            minutes = int(duration_minutes) if duration_minutes else 5
        except (ValueError, TypeError):
            minutes = 5
        expiry = timezone.now() + timedelta(minutes=minutes)
        shared_link = SharedLink.objects.create(
            file=file_obj,
            expires_at=expiry
        )
        relative_url = reverse('public-download', kwargs={'token': shared_link.token})
        full_url = request.build_absolute_uri(relative_url)
        return {
            "download_url": full_url,
            "filename": file_obj.filename,
            "expires_at": shared_link.expires_at
        }