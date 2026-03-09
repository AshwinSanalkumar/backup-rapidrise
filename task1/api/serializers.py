from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Product, UserFile

User = get_user_model()

# SERIALIZER FOR AUTHENTICATION 
class RegisterSerializer(serializers.ModelSerializer):
    """
    User Registration Serializer
    """
    first_name=serializers.CharField(max_length=150,required=True)
    last_name=serializers.CharField(max_length=150)
    email = serializers.EmailField(required=True)
    password=serializers.CharField(write_only=True, min_length=8)
    password_confirm=serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'email', 'first_name', 'last_name']    

    def validate(self, data):

        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields must match."})
        return data
    
    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
    
# SERIALIZER FOR PRODUCT CRUD 
class ProductSerializer(serializers.ModelSerializer):
    """
    Product Serializer
    """
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Product
        fields = [
            'id', 
            'owner_username', 
            'name', 
            'description', 
            'price', 
            'stock_quantity', 
            'image', 
            'is_deleted', 
            'deleted_at', 
            'created_at'
        ]
        read_only_fields = [
            'id', 
            'owner_username', 
            'is_deleted', 
            'deleted_at', 
            'created_at'
        ]

    def validate_price(self, value):
        """Ensure the product price is not negative."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock_quantity(self, value):
        """Ensure stock is a positive number."""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value
    
# SERIALIZER FOR FILE UPLOAD DOWNLOAD   
class UserFileSerializer(serializers.ModelSerializer):
    """
    File Serializer
    """
    size_readable = serializers.SerializerMethodField()
    class Meta:
        model = UserFile
        fields = ['id', 'filename', 'file_size_bytes', 'size_readable', 'mime_type', 'uploaded_at']
        read_only_fields = ['id', 'file_size_bytes', 'mime_type', 'uploaded_at']
        

    def get_size_readable(self, obj):
        num = float(obj.file_size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if num < 1024.0:
                return f"{num:.2f} {unit}"
            num /= 1024.0
        return f"{num:.2f} TB"