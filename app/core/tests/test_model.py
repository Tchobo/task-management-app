from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from core import models
def create_user(email="user@example.com", password='tastpass'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelsTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successfull."""
        email = 'test@example.com'
        password = 'testpass123)'
        user= get_user_model().objects.create_user(

            email=email,
        password=password
        )

        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Test email is normalized for new users."""
        simple_emails =[
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['test2@EXAMPLE.com', 'test2@example.com'],
            ['test3@EXAMPLE.com', 'test3@example.com'],
            ['test4@EXAMPLE.com', 'test4@example.com'],
        ]

        for email, expected in simple_emails:
            user = get_user_model().objects.create_user(
                email= email, password='pass123'
            )
            self.assertEqual(user.email,expected )

    def test_new_user_without_email_raises_error(self):
        """ Test that creating a user without an email raises a value error"""

        with self.assertRaises(ValueError):

             get_user_model().objects.create_user('', 'testpass123')
     
    def test_create_superuser(self):
        """Test creating a superuser."""

        email = 'ricos@gmail.com'
        password = 'ricos123'
        user = get_user_model().objects.create_superuser(email, password)
        self.assertEqual(user.email, email)
        self.assertEqual(user.is_staff, True)
        self.assertEqual(user.is_superuser, True)
        self.assertTrue(user.check_password(password), email)

    def test_create_dashboard(self):
        """Test creating dashboard is successful."""
        user = create_user()
        dashboard = models.Dashboard.objects.create(
            user=user, bordName='dashboard1', bordDescription='test descriptif', bordBack = '#232323'
        )

        self.assertEqual(str(dashboard), dashboard.bordName)