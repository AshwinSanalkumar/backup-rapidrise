from django.urls import path
from calculator.views import RegisterView ,LogoutView, AdditionView, SubtractionView, DivisionView, MultiplicationView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns=[
    #Authentication APIs Using JWT
    path('register/',RegisterView.as_view(),name='register'),
    path('refresh/',TokenRefreshView.as_view(),name="token_refresh"),
    path('login/',TokenObtainPairView.as_view(),name='token_obtain'),
    path('logout/', LogoutView.as_view(), name='logout'),

    #ARITHMETIC OPERATIONS
    path('calculate/sum/<str:num1>/<str:num2>/',AdditionView.as_view(),name='add-operation'),
    path('calculate/difference/<str:num1>/<str:num2>/',SubtractionView.as_view(),name='sub-operation'),
    path('calculate/divide/<str:num1>/<str:num2>/',DivisionView.as_view(),name='div-operation'),
    path('calculate/multiply/<str:num1>/<str:num2>/',MultiplicationView.as_view(),name='mul-operation'),
]