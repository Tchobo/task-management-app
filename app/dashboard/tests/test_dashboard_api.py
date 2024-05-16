"""
Test for ingredient API
"""


from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from dashboard.serializers import DashboardSerializer
from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Dashboard, TaskCategorie)

DASHBOARD_URL = reverse('dashboard:dashboard-list')
DASHBOARD_CREATE = reverse('dashboard:dashboard-create')


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

def detail_patch_url(dashboard_id):
    """ Create and return a dashbord detail."""
    return reverse('dashboard:dashboard-patch', args=[dashboard_id])


def detail_update_url(dashboard_id):
    """ Create and return a dashbord detail."""
    return reverse('dashboard:dashboard-update', args=[dashboard_id])
def detail_delete_url(dashboard_id):
    """ Create and return a dashbord detail."""
    return reverse('dashboard:dashboard-delete', args=[dashboard_id])


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

class PublicDashboardApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):    
        """Test auth is required for retrieving dashboard."""
        res = self.client.get(DASHBOARD_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateDashboardApiTest(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
       

    def test_retrieve_dashboards(self):
        """Test rertrieving a list of dashboard"""
        
        Dashboard.objects.create(user=self.user, bordName='My board', bordDescription='This is my first board description', bordBack='#ffffff' )
        Dashboard.objects.create(user=self.user, bordName='My other board ', bordDescription='This is my second board description', bordBack='#f1f1f1' )
       
        res = self.client.get(DASHBOARD_URL)
        dashboards = Dashboard.objects.all()
        serializer = DashboardSerializer(dashboards, many=True)

        self.assertEqual(res.status_code,  status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_dashboard_limited_to_user(self):
        """Test list of dashboard is limited to authenticated user"""

        user2= create_user(email='user2@example.com')
        Dashboard.objects.create(user=user2, bordName='User 2 Board', bordDescription='This is my board description', bordBack='#000000')
        dashboard = Dashboard.objects.create(user=self.user,  bordName='User 1 board', bordDescription='This is my third board description', bordBack='#ffffff')
        res = self.client.get(DASHBOARD_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['bordName'], 'User 1 board')

        self.assertEqual(res.data[0]['bordBack'], '#ffffff')
        self.assertEqual(res.data[0]['bordDescription'], 'This is my third board description')


    def test_update_dashboard(self):
        dashboard = Dashboard.objects.create(user=self.user, bordName='User 3 Board',  bordDescription='This is another board description', bordBack='#ffffff')
        payload = {'bordName': 'TASKO'}

        url = detail_patch_url(dashboard.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK )
        dashboard.refresh_from_db()
        self.assertEqual(dashboard.bordName, payload['bordName'])

    def test_delete_dashboard(self):
        """Test deleting a dashboard."""
        dashboard= Dashboard.objects.create(user=self.user,  bordName='User 4 Board', bordDescription='This is my board description', bordBack='#000000')
        url = detail_delete_url(dashboard.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        dashboards =Dashboard.objects.filter(user=self.user)
        self.assertFalse(dashboards.exists())



    def test_create_dashboard(self):
        """Test creating a dashboard"""

        payload = {
            'user' : self.user,
            'bordName': 'User board Name',
            'bordDescription' : 'My description',
            'bordBack' : '#121288'
        }
        res = self.client.post(DASHBOARD_CREATE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        dashboard = Dashboard.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(dashboard, key), value)
        self.assertEqual(dashboard.user, self.user)


    def test_update_user_returns_error(self):
        """ Test changing the dashboard user results in an error """
        new_user = create_user(email='user3@example.com', password='test123')
        dashboard = create_dashboard(user=self.user)
        payload = {'user': new_user.id}
        url = detail_patch_url(dashboard.id)
        self.client.patch(url, payload)
        dashboard.refresh_from_db()
        self.assertEqual(dashboard.user, self.user)



    def test_dashboard_other_users_dashboard_error(self):
        """Test trying to delete another users dashboard gives error."""
        new_user = create_user(email='user3@example.com', password='test123')
        dashboard=create_dashboard(user=new_user)
        url = detail_delete_url(dashboard.id)
        res = self.client.delete(url)
       
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        self.assertTrue(Dashboard.objects.filter(id=dashboard.id).exists())

   



    def test_create_dashboard_with_new_categories(self):
        """Test creating a dashboard with new category"""

        payload = {
            'bordName': 'Board with category',
            'bordDescription': 'Board with category description',
            'bordBack': '#002211',
           
        }
        res = self.client.post(DASHBOARD_CREATE, payload, format='json')
        
        # Check if the response status is HTTP 201 Created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        # Check if a dashboard is created for the user
        dashboards = Dashboard.objects.filter(user=self.user)
        self.assertEqual(dashboards.count(), 1)
    

       
    
  



         

        

        


