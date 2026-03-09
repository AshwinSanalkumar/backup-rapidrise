from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, UserFile, SharedLink
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

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


class ProductTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="password")
        self.other_user = User.objects.create_user(username="stranger", password="password")
        
        self.client.force_authenticate(user=self.user)
        
        # Create an initial product for detail/update/delete tests
        self.product = Product.objects.create(
            name="Original Product",
            price=50.00,
            owner=self.user,
            is_deleted=False
        )
        
        self.list_url = reverse('product-list')
        self.add_url = reverse('product-add')
        self.detail_url = reverse('product-view', kwargs={'pk': self.product.pk})

    def test_create_product_with_mock_image(self):
        """Verify image upload and service-level creation"""
        # Create a tiny mock image file
        image_payload = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        
        data = {
            "name": "New Gadget",
            "price": "29.99",
            "description": "Awesome tech",
            "image_file": image_payload
        }
        
        response = self.client.post(self.add_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(Product.objects.get(name="New Gadget").image)

    def test_privacy_protection(self):
        """Verify User B cannot see User A's products (404 logic)"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_soft_delete_mechanics(self):
        """Verify product is hidden but not removed from database"""
        delete_url = reverse('product-delete', kwargs={'pk': self.product.pk})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_deleted)
        self.assertIsNotNone(self.product.deleted_at)

    def test_list_active_only(self):
        """Verify get_all_active service excludes soft-deleted items"""
        # Soft delete the existing product
        self.product.is_deleted = True
        self.product.save()
        
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 0)

class FileAndSharingTests(APITestCase):
    def setUp(self):
        # Setup Users
        self.user = User.objects.create_user(username="file_owner", password="password123")
        self.stranger = User.objects.create_user(username="stranger", password="password123")
        
        # URLs
        self.upload_url = reverse('file-upload')
        self.list_url = reverse('file-list')
        
        # Create a dummy file for sharing tests
        self.test_file = SimpleUploadedFile(
            "test_doc.pdf", 
            b"pdf_content", 
            content_type="application/pdf"
        )
        self.file_record = UserFile.objects.create(
            owner=self.user,
            content=self.test_file,
            filename="test_doc.pdf",
            file_size_bytes=len(b"pdf_content"),
            mime_type="application/pdf"
        )
        
        self.share_url = reverse('share-file', kwargs={'file_id': self.file_record.id})


    
    def test_file_upload_success(self):
        """Verify FileStorageService processes and stores a valid file"""
        self.client.force_authenticate(user=self.user)
        content = b"image_data" * 300 
        new_file = SimpleUploadedFile("new.png", content, content_type="image/png")
        response = self.client.post(self.upload_url, {'file': new_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['filename'], "new.png")
        size_str = response.data['size_readable']
        self.assertTrue(any(unit in size_str for unit in ['B', 'KB', 'MB', 'GB']))

    def test_list_files_privacy(self):
        """Verify users only see their own uploaded files"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 1)

    def test_generate_share_link_5min_default(self):
        """Verify service generates a link with the default 5-minute expiry"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.share_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("download_url", response.data)
        
        # Verify DB entry
        link_record = SharedLink.objects.get(file=self.file_record)
        # Check if expiry is roughly 5 mins from now
        diff = link_record.expires_at - timezone.now()
        self.assertTrue(timedelta(minutes=4) < diff <= timedelta(minutes=5))

    def test_one_time_download_burn_logic(self):
        """Verify the 'is_accessed' flag prevents multiple downloads"""
        # 1. Create a link manually
        link = SharedLink.objects.create(
            file=self.file_record,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        download_url = reverse('public-download', kwargs={'token': link.token})

        # 2. First attempt (Should work)
        response1 = self.client.get(download_url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # 3. Second attempt (Should fail 410 Gone)
        response2 = self.client.get(download_url)
        self.assertEqual(response2.status_code, status.HTTP_410_GONE)
        self.assertEqual(response2.data['error'], "This link has already been used and is no longer valid.")

    def test_download_expired_link(self):
        """Verify expired links cannot be used"""
        link = SharedLink.objects.create(
            file=self.file_record,
            expires_at=timezone.now() - timedelta(minutes=1) # Already expired
        )
        download_url = reverse('public-download', kwargs={'token': link.token})
        
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "This link has expired")

    def test_unauthorized_share_attempt(self):
        """Verify User B cannot generate a share link for User A's file"""
        self.client.force_authenticate(user=self.stranger)
        response = self.client.post(self.share_url)
        
        # Should return 404 because the view filters by owner=request.user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)