from django.db import models

# Create your models here.
from django.conf import settings
import uuid
from django.contrib.postgres.fields import ArrayField

from django.contrib.auth.models import (
    AbstractBaseUser,
      BaseUserManager,
        PermissionsMixin,

)
import uuid 
import os


def profile_image_file_path(instance, filename):
    """Generating file path for new recipe image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'profile', filename)


def task_image_file_path(instance, filename):
    """Generating file path for new task image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'tasks', filename)


class UserManager(BaseUserManager):
    """Manager for user """

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("You must have an email adresse.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user=self.create_user(email, password)
        user.is_staff=True
        user.is_superuser =True
        user.is_active =True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email= models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=True)
    phone_number=models.CharField(max_length=12, blank=True, default=True)
    profile_image=models.ImageField(null=True, upload_to=profile_image_file_path)
    code_activation= models.CharField(max_length=8, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'



class ActiveToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.token}"
    


class Dashboard(models.Model):
  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    bordName = models.CharField(max_length=255, blank=True, null=True)
    bordDescription = models.TextField(blank=True, null=True)
    bordBack = models.CharField(max_length=20, blank=True, null=True)
    #task_Categorie = models.ManyToManyField("TaskCategorie")
    slug = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.bordName}"
    

class TaskCategorie(models.Model):
    name = models.CharField(max_length=100)
    indexColor = models.CharField(max_length=200)
    indexNumber = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)

    defaultTaskCategory = models.BooleanField(default=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, null=True, blank=True, related_name="categories")

    class Meta:
        ordering = ['indexNumber']
    def __str__(self):
        return f"{self.name}"
    



    

    
class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    tags = ArrayField(models.CharField(max_length=200), blank=True)
    badgeColor = ArrayField(models.CharField(max_length=200), blank=True)
    created  = models.DateTimeField(auto_now_add=True, blank=True)
    deadline = models.DateField(blank=True)
    #taskComments = models.ManyToManyField(TaskComment)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    #files_list = models.ManyToManyField(MediaFile)
    #task_file =models.FileField(upload_to=task_image_file_path, null=True, blank=True)
    taskCategorie = models.ForeignKey(TaskCategorie, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks")
    position = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True, default=0.0000)

    class Meta:
        ordering = ['position']

class TaskComment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    

class MediaFile(models.Model):
    file =models.FileField(upload_to=task_image_file_path)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="files")





    


