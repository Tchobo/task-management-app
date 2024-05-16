"""
Serializers for the user API VIew
"""

from django.contrib.auth import (get_user_model, authenticate)
from rest_framework import serializers
from core.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken
from account.email import send_opt_via_mail
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length':5}, 'code_activation':{'write_only': True}}


    def create(self, validate_date):
        """Create and return a user with encrypted password."""
        user = get_user_model().objects.create_user(**validate_date)
       
        send_opt_via_mail(user.email)

        return user
    
    def update(self, instance, validate_data):
        """Update and return user."""
        password= validate_data.pop('password', None)
        user = super().update(instance, validate_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserDetailSerializer(UserSerializer):
    """Serializer for recipe detail view."""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['id', 'profile_image']


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style = {'input_type':'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)

            if not user:
                msg = "Votre adresse e-mail n'a pas encore été vérifiée ou est incorrect. Veuillez consulter votre boîte de réception pour le lien de vérification. Si vous ne trouvez pas l'e-mail, veuillez vérifier votre dossier de courrier indésirable."
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs



class UserImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to user."""

    class Meta:
        model = User
        fields= ['id', 'profile_image']
        read_only_fields = ['id']
        extra_kwargs = {'profile_image': {'required':'True'}}



class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code_activation = serializers.CharField()