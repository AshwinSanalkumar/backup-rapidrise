from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

User = get_user_model()

#AUTHENTICATION SERVICES
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

#ARITHMETIC OPERATION SERVICES
class ArithmeticService:
    @staticmethod
    def add(num1,num2):
        try:
            return float(num1) + float(num2)
        except (ValueError,TypeError):
            return None
        
    @staticmethod
    def difference(num1,num2):
        try:
            return float(num1) - float(num2)
        except (ValueError,TypeError):
            return None
        
    @staticmethod
    def quotient(num1 , num2):
        try:
            if float(num2)==0:
                return None
            return float(num1) / float (num2)
        except (ValueError,TypeError):
            return None
    
    @staticmethod
    def product(num1,num2):
        try:
            return float(num1) * float(num2)
        except (ValueError,TypeError):
            return None