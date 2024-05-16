from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
import tempfile
import os
from unittest.mock import patch
from PIL import Image


CREATE_USER_URL  =reverse('account:create')
TOKEN_URL = reverse('account:token')
ME_URL = reverse('account:me')
VERIFY_OTP_URL = reverse('account:verify')

#USER_VERIFY_URL = reverse('account:verify')
#ME_URL = reverse('account:me')
def image_upload_url(user_id):
    """Create and return an image upload URL."""
    return reverse('account:upload-image', kwargs={'pk': user_id})

def create_user(**kwargs):
    """ Create and return a new user. """
    user = get_user_model().objects.create_user(**kwargs)
    user.is_active =True
    user.save()
    return user

class PublicAccountApiTests(TestCase):
    """ Test the public features of the user API """

    def setUp(self):
        self.client = APIClient()
        self.user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
       
   
    def test_create_user_success(self):
        """Test creating a user is successful"""

        res = self.client.post(CREATE_USER_URL, self.user_details)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Check if user is created
        user = get_user_model().objects.filter(email=self.user_details['email']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, self.user_details['name'])
        self.assertTrue(user.check_password(self.user_details['password']))
        self.assertNotIn('password', res.data)


    def test_verify_otp_and_activate_user(self):
        """Test verifying OTP and activating the user"""

        # Create a user and get the OTP code
        user = get_user_model().objects.create_user(**self.user_details)
        # Generate a mock OTP code for testing
        otp_code = '1234'

        # Set the OTP code for the user
        user.code_activation = otp_code
        user.save()

        # Verify OTP for the user
        otp_data = {
            'email': self.user_details['email'],
            'code_activation': otp_code,
        }
   
        res = self.client.post(VERIFY_OTP_URL, otp_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Refresh the user from the database and check if is_active is True
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    

    
    """     @patch('account.email.send_opt_via_mail')
    def test_send_email_on_user_creation(self, mock_send_opt_via_mail):
       

        res = self.client.post(CREATE_USER_URL, self.user_details)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Check if send_opt_via_mail was called with the correct email
        mock_send_opt_via_mail.assert_called_once_with(self.user_details['email']) """

    

   
    
    
    def test_user_with_email_exists_error(self):
        payload = {
            'email':'test@example.com',
            'password':'testpass123',
            'name':'Test Name'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_password_too_short_error(self):
        """ Test an error is returned if password less than 5 chars."""
        payload = {
            'email':'test@example.com',
            'password':'pw',
            'name' : 'Test name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
    

    def test_create_token_for_user(self):
        """Test generates token for valid credential"""
        user_details = {
            'name' : 'Test Name',
            'email' : 'test@example.com',
            'password': 'test-user-password123',
        }
        user = create_user(**user_details)

        payload ={
          'email':  user_details['email'],
          'password' : user_details['password']
        } 

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(Token.objects.filter(user=user).exists())
        token =Token.objects.get(user=user)
        self.assertEqual(res.data['token'], token.key)

    def test_create_token_bad_credentials(self):
        create_user(email='test@example.com', password='goodpass')
        payload={  'email':'test@example.com', 'password' : 'badpass'}
        res =self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        # Test posting a blank password returns en error.
        payload = { 'email':'test@example.com', 'password':''}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateUserApiTests(TestCase):
    """Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )

        self.client = APIClient()
        self.client.force_authenticate(user= self.user)

    def test_retrieve_profile_success(self):
       
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name':self.user.name,
            'email':self.user.email,

     })
        
    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""

        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""

        payload = {
            'name':'Update name',
            'password':'newpassword123'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)




