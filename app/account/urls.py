"""
Url mappings fro the user API
"""
from django.urls import path
from account import views
from rest_framework.routers import DefaultRouter




app_name = 'account'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CustomObtainAuthToken.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('create/<int:pk>/upload-image/', views.UserImageUploadView.as_view(), name='upload-image'),
    path('verify/', views.VerifyOTPView.as_view(), name='verify'),

]



