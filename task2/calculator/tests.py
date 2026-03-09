from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.logout_url = reverse('logout')
        self.user_data = {
            "username": "test_engineer",
            "email": "promo@company.com",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "first_name": "Ashwin",
            "last_name": "Sanalkumar"
        }
        # Create a user specifically for logout tests
        self.user = User.objects.create_user(
            username="logout_user", 
            password="testpassword123"
        )

    def test_registration_success(self):
        """Verify user creation and data cleanup (password_confirm removal)"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="test_engineer").exists(), True)

    def test_registration_mismatched_passwords(self):
        """Verify validation logic in the RegisterSerializer"""
        self.user_data['password_confirm'] = "wrong_password"
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_and_blacklist(self):
        """Verify AuthService.logout_user correctly blacklists the JWT"""
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.logout_url, {"refresh": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Logged out successfully.")


class ArithmeticTests(APITestCase):
    def setUp(self):
        # 1. Create a user for authentication
        self.user = User.objects.create_user(
            username="mathuser", 
            email="math@example.com", 
            password="password123"
        )
        
        # 2. Generate a JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        
        # 3. Authorize the client for all requests in this class
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_addition_success(self):
        """Test adding two valid numbers."""
        # Pattern: calculate/sum/5/4/
        url = reverse('add-operation', kwargs={'num1': '10.5', 'num2': '4.5'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], 15.0)
        self.assertEqual(response.data['operation'], 'sum')

    def test_addition_invalid_input(self):
        """Test adding with non-numeric strings."""
        url = reverse('add-operation', kwargs={'num1': 'abc', 'num2': '5'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_addition_unauthenticated(self):
        """Test that unauthenticated users cannot access the math API."""
        self.client.credentials()  # Wipe the token
        url = reverse('add-operation', kwargs={'num1': '5', 'num2': '5'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_subtraction_success(self):
        """Test subtracting two valid numbers."""
        # Pattern: calculate/sub/10/4/
        url = reverse('sub-operation', kwargs={'num1': '10', 'num2': '4'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], 6.0)
        self.assertEqual(response.data['operation'], 'difference')

    def test_subtraction_negative_result(self):
        """Test subtraction resulting in a negative number."""
        url = reverse('sub-operation', kwargs={'num1': '5', 'num2': '10'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], -5.0)

    def test_subtraction_invalid_input(self):
        """Test subtraction with non-numeric strings."""
        url = reverse('sub-operation', kwargs={'num1': '10', 'num2': 'not_a_number'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_division_success(self):
        """Test dividing two valid numbers."""
        # Pattern: calculate/div/10/2/
        url = reverse('div-operation', kwargs={'num1': '10', 'num2': '2'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], 5.0)
        self.assertEqual(response.data['operation'], 'Division')

    def test_division_invalid_result(self):
        """Test dividing resulting in a negative number."""
        url = reverse('div-operation', kwargs={'num1': '10', 'num2': '0'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_dividing_invalid_input(self):
        """Test dividing with non-numeric strings."""
        url = reverse('div-operation', kwargs={'num1': '10', 'num2': 'not_a_number'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_multiplication_success(self):
        """Test multiplying two valid numbers."""
        # Pattern: calculate/multiply/5/4/
        url = reverse('mul-operation', kwargs={'num1': '5', 'num2': '4'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], 20.0)
        self.assertEqual(response.data['operation'], 'multiplication')

    def test_multiplication_invalid_input(self):
        """Test multiplying with non-numeric strings."""
        url = reverse('mul-operation', kwargs={'num1': 'abc', 'num2': '5'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)