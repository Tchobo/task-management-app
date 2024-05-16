"""
Test for ingredient API
"""


from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from tasks.serializers import TaskCommentSerializer
from rest_framework import status
from rest_framework.test import APIClient
import datetime
from core.models import (Task, TaskComment)

COMMENT_URL = reverse('tasks:taskcomment-list')
COMMENT_CREATE = reverse('tasks:taskcomment-create')


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

def detail_patch_url(taskcomment_id):
    """ Create and return a taskcomment detail."""
    return reverse('tasks:taskcomment-patch', args=[taskcomment_id])


def detail_update_url(taskcomment_id):
    """ Create and return a taskcomment detail."""
    return reverse('tasks:taskcomment-update', args=[taskcomment_id])
def detail_delete_url(taskcomment_id):
    """ Create and return a taskcomment detail."""
    return reverse('tasks:taskcomment-delete', args=[taskcomment_id])


def create_task(user, **params):
    """Create and return a sample task"""
    today = datetime.date.today()
    tomorrow =  today +datetime.timedelta(days=1)

    defaults = {
        'title':'Renommé utilisateur en users',
        'description':'Sample description',
        'tags':['corriger le lien', 'renommé'],     
        'badgeColor':['#332233', '#121212'],
        'deadline' : tomorrow

       
        #'taskComments' :[ {'title':"comment ça va"}, {'title': 'ça va bien'}]
          

    }
    defaults.update(params)

    task = Task.objects.create(creator=user, **defaults)
    return task



def create_comment(user, **params):
    """Create and return a sample comment"""
   
    defaults = {
        'text':'Sample comment',
          
    }
    defaults.update(params)

    taskComment = TaskComment.objects.create(user=user, **defaults)
    return taskComment

class PublicTaskCommentApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):    
        """Test auth is required for retrieving task comment."""
        res = self.client.get(COMMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)




class PrivateCommentApiTests(TestCase):

    def setUp(self):
        self.user= create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_comments(self):
        """Test retrieving a list of comments"""
        task = create_task(user=self.user)
        TaskComment.objects.create(user=self.user,text="J'ai besoins de détail par apport au fichier Y", task=task)
        TaskComment.objects.create(user=self.user,text="Un instant.", task=task)
        res = self.client.get(COMMENT_URL)
     
        comments = TaskComment.objects.all()
        serializer= TaskCommentSerializer(comments, many=True)
        self.assertEqual(res.status_code,  status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        

    def test_patch_task_comment(self):
        task = create_task(user=self.user)
        taskComment = TaskComment.objects.create(user=self.user, text='User 3 text', task=task)
        payload = {'text': 'TASKO is good'}

        url = detail_patch_url(taskComment.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK )
        taskComment.refresh_from_db()
        self.assertEqual(taskComment.text, payload['text'])


    def test_delete_comment(self):
        """Test deleting a commentaire."""
        task = create_task(user=self.user)
        testComment= TaskComment.objects.create(user=self.user,  text='User 4 comment', task=task)
        url = detail_delete_url(testComment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        taskComments =TaskComment.objects.filter(user=self.user)
        self.assertFalse(taskComments.exists())


    def test_create_task_commentaire(self):
        """Test creating a commentaire"""
        task = create_task(user=self.user)
        print("task created ", task)
        payload = {
        'user': self.user.id,  # Utilisez l'ID de l'utilisateur
        'text': 'My description',
        'task': task.id,  # Utilisez l'ID de la tâche
    }
        res = self.client.post(COMMENT_CREATE, payload)
        print("Response data:", res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        commentaire = TaskComment.objects.get(id=res.data['id'])
        for key, value in payload.items():
            if key == 'user':
                self.assertEqual(getattr(commentaire, key).id, value)  # Comparez les IDs des utilisateurs
            elif key == 'task':
                self.assertEqual(getattr(commentaire, key).id, value)  # Comparez les IDs des tâches
            else:
                self.assertEqual(getattr(commentaire, key), value)
            
    def test_update_user_returns_error(self):
        """ Test changing the taskComment user results in an error """
        new_user = create_user(email='user3@example.com', password='test123')
        taskComment = create_comment(user=self.user)
        payload = {'user': new_user.id}
        url = detail_patch_url(taskComment.id)
        self.client.patch(url, payload)
        taskComment.refresh_from_db()
       
        self.assertEqual(taskComment.user, self.user)