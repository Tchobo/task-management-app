"""
Test for ingredient API
"""


from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from dashboard.serializers import DashboardSerializer, TaskCategorieSerializer
from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Dashboard, TaskCategorie)

CATEGORY_URL = reverse('dashboard:category-list')
CATEGORY_CREATE = reverse('dashboard:category-create')


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

def detail_patch_url(category_id):
    """ Create and return a category detail."""
    return reverse('dashboard:category-patch', args=[category_id])


def detail_update_url(category_id):
    """ Create and return a category detail."""
    return reverse('dashboard:category-update', args=[category_id])
def detail_delete_url(category_id):
    """ Create and return a category detail."""
    return reverse('dashboard:category-delete', args=[category_id])

def create_dashboard(user, **params):
    """Create and return a sample dashboard"""

    defaults = {
        'bordName':'Sample dashboard name',
        'bordDescription':'Sample description',
        'bordBack':"#123456"     
    }
    defaults.update(params)

    dashboard = Dashboard.objects.create(user=user, **defaults)
    return dashboard


class PublicTaskCateroryApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):    
        """Test auth is required for retrieving category."""
        res = self.client.get(CATEGORY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTests(TestCase):

        def setUp(self):
            self.user= create_user()
            self.client = APIClient()
            self.client.force_authenticate(self.user)

        def test_retrieve_categories(self):
            """Test retrieving a list of categories"""
            dashboard= Dashboard.objects.create(user=self.user,  bordName='User 4 Board', bordDescription='This is my board description', bordBack='#000000')


            TaskCategorie.objects.create(name='In progress', indexColor="#121222", indexNumber=1.003,defaultTaskCategory=True, dashboard=dashboard)
            TaskCategorie.objects.create(name='Done', indexColor="#121222", indexNumber=2.003, defaultTaskCategory=True, dashboard=dashboard)

            res = self.client.get(CATEGORY_URL)
            categories = TaskCategorie.objects.all().order_by('-name')
            serializer= TaskCategorieSerializer(categories, many=True)

            self.assertEqual(res.status_code,  status.HTTP_200_OK)
            self.assertEqual(res.data, serializer.data)


        def test_update_category(self):
            dashboard = create_dashboard(user= self.user)
            category = TaskCategorie.objects.create( name="Processing", indexColor="#121222", indexNumber=3.002, defaultTaskCategory=True, dashboard=dashboard)
            payload = {'name': 'To do'}

            url = detail_patch_url(category.id)
            res = self.client.patch(url, payload)

            self.assertEqual(res.status_code, status.HTTP_200_OK )
            category.refresh_from_db()
            self.assertEqual(category.name, payload['name'])
        
        def test_delete_category(self):
            """Test deleting a catogory."""
            dashboard = create_dashboard(user= self.user)

            category= TaskCategorie.objects.create(name="Done", indexColor="#121222", indexNumber=5.003, defaultTaskCategory=True, dashboard=dashboard)
            url = detail_delete_url(category.id)
            res = self.client.delete(url)
            self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
            categories =TaskCategorie.objects.filter(pk=category.id)
            self.assertFalse(categories.exists())

       
                
