from django.urls import path
from api.views import RegisterView ,LogoutView, ProductListView, ProductCreateView, ProductDetailView, ProductUpdateView, ProductDeleteView, FileUploadView, FileListView, CreateSharedLinkView, PublicDownloadView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns=[
    #Authentication APIs Using JWT
    path('register/',RegisterView.as_view(),name='register'),
    path('refresh/',TokenRefreshView.as_view(),name="token_refresh"),
    path('login/',TokenObtainPairView.as_view(),name='token_obtain'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    #PRODUCTS CRUD APIs
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/add/', ProductCreateView.as_view(), name='product-add'),
    path('products/view/<uuid:pk>/', ProductDetailView.as_view(), name='product-view'),
    path('products/update/<uuid:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('products/delete/<uuid:pk>/', ProductDeleteView.as_view(), name='product-delete'),

    #SECURE FILE UPLOAD DOWNLOAD
    path('files/upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/list/', FileListView.as_view(), name='file-list'),
    path('files/<str:file_id>/generate-link/', CreateSharedLinkView.as_view(), name='share-file'),
    path('file/download/<str:token>/', PublicDownloadView.as_view(), name='public-download'),
]