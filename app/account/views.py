"""
View for the user API
"""
from django.shortcuts import render

# Create your views here.

from account.utils import store_active_token
from core.models import User

from rest_framework import generics, authentication, permissions

from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication

from rest_framework import (viewsets, mixins, status)
from account.serializers import (AuthTokenSerializer, UserImageSerializer, UserDetailSerializer, UserSerializer, VerifyOTPSerializer)
from rest_framework.permissions import IsAuthenticated

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserDetailSerializer

class UserImageUploadView(generics.GenericAPIView):
    """Upload an image for a user."""
    queryset = User.objects.all()
    serializer_class = UserImageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomObtainAuthToken(ObtainAuthToken):
    """Obtain token view"""
    serializer_class=AuthTokenSerializer
    renderer_classes=api_settings.DEFAULT_RENDERER_CLASSES
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Delete existing token, if any
        Token.objects.filter(user=user).delete()

        token, created = Token.objects.get_or_create(user=user)
        
        return Response({'token': token.key}) 
    

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manager the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes= [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
    

class VerifyOTPView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = VerifyOTPSerializer
    def post(self, request, *args, **kwargs):
        data =  request.data
        serializer =  self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
       

        try:
          
            email = serializer.data["email"]
            opt = serializer.data["code_activation"]
           
            user = User.objects.filter(email=email)
            if not user.exists():
                    return Response(
                        {
                            "status": status.HTTP_404_NOT_FOUND,
                            "message": "Cette adresse email n'est pas reconnue",
                            "data": "Email invalid",
                        }
                    )
          
            if not user[0].code_activation == opt:
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Le code que vous avez saisi est incorrect",
                        }
                    )
            
            else:
                user = user.first()
                user.is_active = True
                user.save()
                return Response(
                            {
                                "status": status.HTTP_200_OK,
                                "success": True,
                                "message": "Email vérifié avec succès",
                 
                            },
                              status=status.HTTP_200_OK,
                        )
            
        except Exception as e:
        
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    

