"""
Test for ingredient API
"""


from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from tasks.serializers import TaskSerializer
from rest_framework import status
from rest_framework.test import APIClient
import datetime
from core.models import (Dashboard, Task, TaskCategorie, TaskComment)
import tempfile
import os
from PIL import Image


TASK_URL = reverse('tasks:task-list')
TASK_CREATE = reverse('tasks:task-create')


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

def detail_patch_url(task_id):
    """ Create and return a task detail."""
    return reverse('tasks:task-patch', args=[task_id])

def detail_url(task_id):
    """Create and return a task detail URL"""
    return reverse('tasks:task-detail', args=[task_id])

def detail_update_url(task_id):
    """ Create and return a task detail."""
    return reverse('tasks:task-update', args=[task_id])

def detail_delete_url(task_id):
    """ Create and return a task detail."""
    return reverse('tasks:task-delete', args=[task_id])

def image_upload_url(task_id):
    """Return URL for task image upload"""
    return reverse('tasks:task-upload-image', kwargs={'pk': task_id})

def create_task(user, **params):
    """Create and return a sample task"""
    today = datetime.date.today()
    tomorrow =  today +datetime.timedelta(days=1)

    defaults = {
        'title':'Renommé utilisateur en users',
        'description':'Sample description',
        'tags':['corriger le lien', 'renommé'],     
        'badgeColor':['#332233', '#121212'],
        'deadline' : tomorrow,
       
        #'taskComments' :[ {'title':"comment ça va"}, {'title': 'ça va bien'}]
          

    }
    defaults.update(params)

    task = Task.objects.create(creator=user, **defaults)
    return task


def create_user(**params):
    """Create a new user"""
    return get_user_model().objects.create_user(**params)



class PublictaskAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res =self.client.get(TASK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivatetaskApiTests(TestCase):
    """Test Authentication API request"""
    
    def setUp(self):
        self.client=APIClient()
        self.user = create_user(email='user@example.com', password="test123")
       
        self.client.force_authenticate(self.user)
        tasks = Task.objects.all()
        tasks.delete()
    
    
    def test_retrive_tasks(self):
        """Test retriving a list of tasks"""
        create_task(user=self.user)
        create_task(user=self.user)
        res =self.client.get(TASK_URL)
        task = Task.objects.all().order_by('-title')
        serializer = TaskSerializer(task, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_task_list_limited_to_user(self):
        """Test list of tasks is limited to authenticated user"""
        other_user = create_user(
           email= 'other@gmail.com',
        password='test123'
        )
        create_task(user=other_user)
        create_task(user=self.user)

        res = self.client.get(TASK_URL)
        tasks =Task.objects.filter(creator=self.user)
        serializer=TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_get_task_detail(self):
        """Test get task detail."""
        task = create_task(user=self.user)

        url = detail_url(task.id)
        res = self.client.get(url)
       

        serializer = TaskSerializer(task)
        self.assertEqual(res.data, serializer.data)



    def test_create_task(self):
        """Test creating a task"""
        today = datetime.date.today()
        tomorrow =  today +datetime.timedelta(days=1)
        payload={
        'title':'Couleur orange en users',
        'description':'Sample description',
        'tags':['corriger lien', 'collage'],     
        'badgeColor':['#332233', '#121212'],
        'deadline' : tomorrow,
       
        }
      
        res = self.client.post(TASK_CREATE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data['id'])
       
        for k,v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.creator, self.user)

    def test_partial_update(self):
        """Test partial update of a task"""
       
        task= create_task(
            user= self.user
        )
        payload = {'title':'New checking title'}
        url = detail_patch_url(task.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, payload['title'])
        self.assertEqual(task.creator, self.user)

    def test_full_update_task(self):
        """Test full update of task"""
        today = datetime.date.today()
        tomorrow =  today +datetime.timedelta(days=3)
        task = create_task(
            user=self.user, 
            title='testing the endpoint',
            tags=['recopier le lien', 'supprimer l\'accès'],
            badgeColor = ['#123123', '#123134']
   
        )

        print("task ", task)

        payload ={
            'title' : 'creating the endpoint',
            'tags' : ['modifier le lien'],
            'badgeColor' : ['#123123', '#123134'],
            'deadline' : tomorrow,
            'description' : 'A faire de toute urgence'
        }

        url = detail_update_url(task.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code , status.HTTP_200_OK)

        task.refresh_from_db()

        for k , v in payload.items():
            self.assertEqual(getattr(task, k), v)

        self.assertEqual(task.creator, self.user)



    def test_update_user_returns_error(self):
        """ Test changing the task user results in error """
        new_user = create_user(email='user2@example.com', password='test123')
        task  = create_task(user=self.user)
        payload = { 'user':new_user.id}
        url = detail_patch_url(task.id)
        self.client.patch(url, payload)
        task.refresh_from_db()

        self.assertEqual(task.creator, self.user)



    def test_delete_task(self):
        """Test deleting a task successfull."""
        task = create_task(user=self.user)
        url = detail_delete_url(task.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())


    def test_delete_other_users_task_error(self):
        """Test trying to delete another users task gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        task=create_task(user=new_user)
        url = detail_delete_url(task.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    def test_create_task_with_task_categorie(self):
        """Test creating a commentaire"""
        dashboard= Dashboard.objects.create(user=self.user,  bordName='User 4 Board', bordDescription='This is my board description', bordBack='#000000')
      

        taskCategorie= TaskCategorie.objects.create(name='In progress', indexColor="#121222", indexNumber=1,defaultTaskCategory=True, dashboard=dashboard)
        #task = create_task(user=self.user, taskCategorie=taskCategorie.id)
        print("le task categorie ", taskCategorie.id)
       
        today = datetime.date.today()
        tomorrow =  today +datetime.timedelta(days=1)
        payload={
        'title':'Couleur orange en users',
        'description':'Sample description',
        'tags':['corriger lien', 'collage'],     
        'badgeColor':['#332233', '#121212'],
        'deadline' : tomorrow,
        'taskCategorie':taskCategorie.id,
       
        }
        res = self.client.post(TASK_CREATE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data['id'])
        print("ce qui est créé", res.data)
        for k,v in payload.items():
            if k == 'taskCategorie':
             
                self.assertEqual(getattr(task, k).id, v)  # Comparez les IDs des task categorie
    
            else:
                self.assertEqual(getattr(task, k), v)
            
    def test_task_categorie_on_task(self):
        """Update task_categorie on task"""
        task= create_task(
            user= self.user
        )
        dashboard= Dashboard.objects.create(user=self.user,  bordName='User 4 Board', bordDescription='This is my board description', bordBack='#000000')
      

        taskCategorie= TaskCategorie.objects.create(name='In progress', indexColor="#121222", indexNumber=1,defaultTaskCategory=True, dashboard=dashboard)
        payload = {'taskCategorie':taskCategorie.id}
        url = detail_patch_url(task.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.taskCategorie.id, payload['taskCategorie'])




class ImageUploadTests(TestCase):
    
    """Test for the image upload API"""


    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )

        self.client.force_authenticate(self.user)
        self.task = create_task(user=self.user)

    def tearDown(self):
        # Remove the task from the files' list of related tasks
        for file_obj in self.task.files.all():
            file_obj.tasks.remove(self.task)
             # Delete the related files (if needed)
        self.task.files.clear()

        # Delete the task itself
        self.task.delete()


    def test_upload_image(self):
        """Test uploading an image to a task"""
        task=create_task(user=self.user)
        url = detail_patch_url(task.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
             # Create files_list data (list of dictionaries with 'id' and 'file' keys)
            today = datetime.date.today()
            tomorrow =  today +datetime.timedelta(days=3)
            payload={
           
            'uploaded_files':[image_file]
        }

          # Include files_list in the payload
            res = self.client.patch(url, payload, format='multipart')

        self.assertTrue('id' in res.data)

        task_id = res.data['id']
        # Fetch the task object again to ensure it reflects the latest state
        task.refresh_from_db()
        self.assertTrue(task.files.all().exists())  # Check if files exist after upload

        # Print some debug information
      