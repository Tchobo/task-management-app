"""
Tests for the Task API.
"""

import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Dashboard, Task, TaskCategorie
from tasks.serializers import TaskSerializer


TASK_URL = reverse("tasks:task-list")
TASK_CREATE = reverse("tasks:task-create")


def create_user(**params):
    """Create and return a new user."""
    defaults = {"email": "user@example.com", "password": "testpass123"}
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def detail_patch_url(task_id):
    return reverse("tasks:task-patch", args=[task_id])


def detail_url(task_id):
    return reverse("tasks:task-detail", args=[task_id])


def detail_update_url(task_id):
    return reverse("tasks:task-update", args=[task_id])


def detail_delete_url(task_id):
    return reverse("tasks:task-delete", args=[task_id])


def image_upload_url(task_id):
    return reverse("tasks:task-upload-image", kwargs={"pk": task_id})


def create_task(user, **params):
    """Create and return a sample task."""
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    defaults = {
        "title": "Renommé utilisateur en users",
        "description": "Sample description",
        "tags": ["corriger le lien", "renommé"],
        "badgeColor": ["#332233", "#121212"],
        "deadline": tomorrow,
    }
    defaults.update(params)
    return Task.objects.create(creator=user, **defaults)


class PublictaskAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call the API."""
        res = self.client.get(TASK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatetaskApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="test123")
        self.client.force_authenticate(self.user)
        Task.objects.all().delete()

    def test_retrive_tasks(self):
        """Test retrieving a list of tasks."""
        create_task(user=self.user)
        create_task(user=self.user)
        res = self.client.get(TASK_URL)
        task = Task.objects.all().order_by("-title")
        serializer = TaskSerializer(task, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_task_list_limited_to_user(self):
        """Test list of tasks is limited to the authenticated user."""
        other_user = create_user(email="other@gmail.com", password="test123")
        create_task(user=other_user)
        create_task(user=self.user)

        res = self.client.get(TASK_URL)
        tasks = Task.objects.filter(creator=self.user)
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_task_detail(self):
        """Test getting a task detail."""
        task = create_task(user=self.user)
        url = detail_url(task.id)
        res = self.client.get(url)
        serializer = TaskSerializer(task)
        self.assertEqual(res.data, serializer.data)

    def test_create_task(self):
        """Test creating a task."""
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        payload = {
            "title": "Couleur orange en users",
            "description": "Sample description",
            "tags": ["corriger lien", "collage"],
            "badgeColor": ["#332233", "#121212"],
            "deadline": tomorrow,
        }
        res = self.client.post(TASK_CREATE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.creator, self.user)

    def test_partial_update(self):
        """Test partial update of a task."""
        task = create_task(user=self.user)
        payload = {"title": "New checking title"}
        url = detail_patch_url(task.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, payload["title"])
        self.assertEqual(task.creator, self.user)

    def test_full_update_task(self):
        """Test full update of a task."""
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=3)
        task = create_task(
            user=self.user,
            title="testing the endpoint",
            tags=["recopier le lien", "supprimer l'accès"],
            badgeColor=["#123123", "#123134"],
        )
        payload = {
            "title": "creating the endpoint",
            "tags": ["modifier le lien"],
            "badgeColor": ["#123123", "#123134"],
            "deadline": tomorrow,
            "description": "A faire de toute urgence",
        }
        url = detail_update_url(task.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.creator, self.user)

    def test_update_user_returns_error(self):
        """Test changing the task creator via API is ignored."""
        new_user = create_user(email="user2@example.com", password="test123")
        task = create_task(user=self.user)
        payload = {"user": new_user.id}
        url = detail_patch_url(task.id)
        self.client.patch(url, payload)
        task.refresh_from_db()
        self.assertEqual(task.creator, self.user)

    def test_delete_task(self):
        """Test deleting a task successfully."""
        task = create_task(user=self.user)
        url = detail_delete_url(task.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_delete_other_users_task_error(self):
        """Test that deleting another user's task returns 404."""
        new_user = create_user(email="user2@example.com", password="test123")
        task = create_task(user=new_user)
        url = detail_delete_url(task.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    def test_create_task_with_assigned_user(self):
        """Test creating a task assigned to another user via assign_To (FK)."""
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        assignee = create_user(email="assignee@example.com", password="test123")

        payload = {
            "title": "Couleur orange en users",
            "description": "Sample description",
            "tags": ["corriger lien", "collage"],
            "badgeColor": ["#332233", "#121212"],
            "deadline": tomorrow,
            "assign_To": assignee.id,
        }
        res = self.client.post(TASK_CREATE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        task = Task.objects.get(id=res.data["id"])
        self.assertEqual(task.assign_To, assignee)
        self.assertEqual(task.creator, self.user)

    def test_create_task_with_task_categorie(self):
        """Test creating a task attached to a category."""
        dashboard = Dashboard.objects.create(
            user=self.user,
            bordName="User 4 Board",
            bordDescription="This is my board description",
            bordBack="#000000",
        )
        taskCategorie = TaskCategorie.objects.create(
            name="In progress",
            indexColor="#121222",
            indexNumber=1,
            defaultTaskCategory=True,
            dashboard=dashboard,
        )
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        payload = {
            "title": "Couleur orange en users",
            "description": "Sample description",
            "tags": ["corriger lien", "collage"],
            "badgeColor": ["#332233", "#121212"],
            "deadline": tomorrow,
            "taskCategorie": taskCategorie.id,
        }
        res = self.client.post(TASK_CREATE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data["id"])
        for k, v in payload.items():
            if k == "taskCategorie":
                self.assertEqual(getattr(task, k).id, v)
            else:
                self.assertEqual(getattr(task, k), v)
