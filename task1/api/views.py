from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .services import AuthService, ProductService ,FileStorageService
from .serializers import RegisterSerializer, ProductSerializer, UserFileSerializer
from .models import Product, UserFile, SharedLink
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import FileResponse
from uuid import UUID

#VIEW FOR AUTHENTICATION
class RegisterView(APIView):
    """
    api: api/register
    View used to Create an User 
    """
    permission_classes=[AllowAny]

    def post (self, request):

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data
        clean_data.pop('password_confirm', None)

        user=AuthService.register_user(clean_data)

        return Response({
            "status":"success",
            "message":f"User {user.first_name} created sucessfully.",
            "data":{
                "id":user.id,
                "email":user.email
            }
        },status=status.HTTP_201_CREATED)
    
class LogoutView(APIView):
    """
    api: api/logout
    View used for TokenBlacklist 
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            AuthService.logout_user(refresh_token)
            return Response(
                {"message": "Logged out successfully."}, 
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#VIEW FOR PRODUCT CRUD
class ProductListView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/products/
    View used for listing all the products that belong to the user
    """
    def get(self, request):
        products = ProductService.get_all_active(request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/products/add/
    View used to add a new Product
    """
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data
        product = ProductService.create_product(
            user=request.user, 
            data=clean_data, 
            image_file=request.FILES.get('image_file')
        )
        
        return Response({
            "status": "success",
            "message": "Product created successfully",
            "data": ProductSerializer(product).data
        }, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/products/view/<product id>/
    View used to get details of a particular product
    """
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, owner=request.user, is_deleted=False)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/products/update/<product id>
    View used to update a Particular product
    """
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk, owner=request.user, is_deleted=False)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_product = ProductService.update_product(
            product=product,
            data=serializer.validated_data,
            image_file=request.FILES.get('image_file')
        )
        return Response(ProductSerializer(updated_product).data)

class ProductDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/products/delete/<product id>
    View used to soft_delete a particular product
    """
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk, owner=request.user, is_deleted=False)
        ProductService.soft_delete_product(product)
        return Response({
            "status": "success",
            "message": "Product moved to trash."
        }, status=status.HTTP_200_OK)

#FILE UPLOAD DOWNLOAD  
class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/files/upload/
    View used file Upload
    """
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_file = FileStorageService.process_and_store_file(
                user=request.user, 
                file_obj=file_obj, 
            ) 
            serializer = UserFileSerializer(new_file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class FileListView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/files/list/
    View used to list files
    """
    def get(self, request):
        files = UserFile.objects.filter(owner=request.user)
        serializer = UserFileSerializer(files, many=True)
        return Response(serializer.data)
    
class CreateSharedLinkView(APIView):
    permission_classes = [IsAuthenticated]
    """
    api: api/files/<file_id>/generate-link/
    View used to Generate Download link
    """
    def post(self, request, file_id):
        try:
            file_uuid = UUID(file_id)
        except ValueError:
            return Response(
                {"error": "Invalid file ID format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_obj = UserFile.objects.get(id=file_uuid, owner=request.user)
            share_data = FileStorageService.create_shareable_data(
                file_obj=file_obj,
                request=request, 
                duration_minutes=request.data.get('duration_minutes')
            )

            return Response(share_data, status=status.HTTP_201_CREATED)

        except UserFile.DoesNotExist:
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        
class PublicDownloadView(APIView):
    permission_classes = [AllowAny]
    """
    api: api/file/download/<token>/
    View used to Download using Secure link
    """
    def get(self,request, token):
        try:
            file_token = UUID(token)
        except ValueError:
            return Response(
                {"error": "Invalid download link format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            shared_link = SharedLink.objects.get(token=file_token)
            if shared_link.is_accessed:
                return Response(
                    {"error": "This link has already been used and is no longer valid."}, 
                    status=status.HTTP_410_GONE
                )
            if timezone.now() > shared_link.expires_at:
                return Response({"error": "This link has expired"}, status=status.HTTP_404_NOT_FOUND)
            shared_link.is_accessed = True
            shared_link.save()
            file_obj = shared_link.file
            response = FileResponse(file_obj.content.open('rb'), content_type=file_obj.mime_type)
            response['Content-Disposition'] = f'attachment; filename="{file_obj.filename}"'
            return response

        except SharedLink.DoesNotExist:
            return Response(
                {"error": "Invalid link."}, 
                status=status.HTTP_404_NOT_FOUND
            )