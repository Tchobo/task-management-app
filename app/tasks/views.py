from django.db.models import Q
from django.shortcuts import render

from core.models import Task, TaskComment, User
from . serializers import  FileSerializer, TaskCommentSerializer,  TaskFileSerializer,  TaskSerializer
from core.models import TaskComment
from rest_framework.response import Response
# Create your views here.
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import TaskCommentSerializer
from django.http import Http404
# Create your views here.
from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi
from drf_spectacular.utils import (
    OpenApiTypes,
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    )

class BasicApi(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get_object(self, pk):
        try:
            return TaskComment.objects.get(pk=pk)
        except TaskComment.DoesNotExist:
            raise Http404
        
    def get_object_task(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404
        

class TaskCommentCreateApiView(BasicApi):
    """Comment post view"""
    serializer_class = TaskCommentSerializer

    def post(self, request):
        data = request.data
        print("task depuis le view ",data['task'])
        serializer = TaskCommentSerializer(data=data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCommentListView(BasicApi):
    """Comment list view"""
    serializer_class = TaskCommentSerializer
    def get(self, requests, pk=None):
        if pk is not None:
            task=self.get_object(pk = pk)
            serializer = TaskCommentSerializer(task)
        else :
            tasks = TaskComment.objects.filter(user=requests.user)
            serializer = TaskCommentSerializer(tasks, many=True)
        return Response(serializer.data)
    

class TaskCommentApiPatchView(BasicApi):  
    serializer_class = TaskCommentSerializer
    
    
        
    def patch(self, request, pk):
        try:
            task_comment = self.get_object(pk)     
        except TaskComment.DoesNotExist:
            raise Http404("TaskComment does not exist")

        serializer = TaskCommentSerializer(task_comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TaskCommentApiDeleteView(BasicApi): 
    """Delete a dashboard view"""
    serializer_class = TaskCommentSerializer
    def delete(self, request, pk):
        taskComment = self.get_object(pk)
     
        if taskComment and taskComment.user.id == request.user.id:
            taskComment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    



class TaskApiCreateView(BasicApi):
    serializer_class = TaskSerializer
    parser_classes = (MultiPartParser,)


    def post(self, request):
        data = request.data

        serializer = TaskSerializer(data=data, context={'request':request})
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TaskListView(BasicApi):
    """Task list view.

    Without a pk, returns every task the authenticated user is involved in —
    either as creator OR as assignee — so that a user can find in one place
    both tasks they own and tasks other people delegated to them.
    """
    serializer_class = TaskSerializer

    def get(self, requests, pk=None):
        if pk is not None:
            task = self.get_object_task(pk=pk)
            serializer = TaskSerializer(task)
        else:
            user = requests.user
            tasks = Task.objects.filter(
                Q(creator=user) | Q(assign_To=user)
            ).distinct()
            serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    

class TaskApiPatchView(BasicApi):
    serializer_class = TaskSerializer   
    def patch(self, request, pk):
        task = self.get_object_task(pk)     
        serializer = TaskSerializer(task, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TaskApiUpdateView(BasicApi):
    serializer_class = TaskSerializer   
    
    def put(self, request, pk):
        task = self.get_object_task(pk)     
        serializer = TaskSerializer(task, data=request.data, context={'request': request},)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TaskApiDeleteView(BasicApi): 
    """Delete a task view"""
    serializer_class = TaskSerializer
    def delete(self, request, pk):
        task = self.get_object_task(pk)
  
    
        if task and task.creator.id == request.user.id:
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
    


class TaskRebalanceCategoryView(BasicApi):
    """Rebalance the ``position`` of every task in a category.

    The task list uses fractional indexing (each task has a Decimal position;
    reordering computes a value between neighbours). After many reorders the
    gap between neighbours can shrink below the DB precision (5 decimals),
    causing silent truncation and identical positions. This endpoint restores
    healthy spacing by reassigning every task's position to a fixed step
    (60000, 120000, 180000, …) while preserving the current visual order.

    URL: POST /api/tasks/rebalance-category/<uuid:category_pk>/
    """

    STEP = 60000

    def post(self, request, category_pk):
        from core.models import TaskCategorie
        try:
            category = TaskCategorie.objects.get(pk=category_pk)
        except TaskCategorie.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        tasks_qs = Task.objects.filter(taskCategorie=category).order_by("position", "created")
        for idx, task in enumerate(tasks_qs, start=1):
            task.position = self.STEP * idx
            task.save(update_fields=["position"])

        return Response(
            {"category": str(category.pk), "rebalanced": tasks_qs.count(), "step": self.STEP},
            status=status.HTTP_200_OK,
        )


class TaskImageUploadView(BasicApi):
    parser_classes = (MultiPartParser,)

    serializer_class = FileSerializer

    
    def post(self, request, pk):
        print("Received data: ", request.data)
        try:
            task = self.get_object_task(pk)
            print("this is the task ", task)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FileSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Validation errors:", serializer.errors)  # Print validation errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)