from django.shortcuts import render
from core.models import Dashboard, TaskCategorie
from rest_framework.response import Response
# Create your views here.
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import DashboardSerializer, TaskCategorieSerializer
from django.http import Http404


class BasicDashboardApi(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get_object(self, slug):
        try:
            return Dashboard.objects.get(slug=slug)
        except Dashboard.DoesNotExist:
            raise Http404
        
    def get_object_by_pk(self, pk):
        try:
            return Dashboard.objects.get(pk=pk)
        except Dashboard.DoesNotExist:
            raise Http404
        
    
        
    def get_category_object(self, pk):
        try:
            return TaskCategorie.objects.get(pk=pk)
        except TaskCategorie.DoesNotExist:
            raise Http404


class DashboardApiListView(BasicDashboardApi):
    serializer_class = DashboardSerializer
    def get(self, requests, slug=None):
        if slug is not None:
            dashboard=self.get_object(slug = slug)
            serializer = DashboardSerializer(dashboard)
        else :
            dashboards = Dashboard.objects.filter(user=requests.user)
            serializer = DashboardSerializer(dashboards, many=True)
        return Response(serializer.data)
    

class DashboardApiCreateView(BasicDashboardApi):
    serializer_class = DashboardSerializer
    
    def post(self, request):
        data = request.data
     

        serializer = DashboardSerializer(data=data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardApiUpdateView(BasicDashboardApi):
    serializer_class = DashboardSerializer   
    def put(self, request, pk):
        dashboard = self.get_object_by_pk(pk)

        if dashboard:
            serializer = DashboardSerializer(dashboard,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardApiPatchView(BasicDashboardApi):  
    serializer_class = DashboardSerializer
    
    
        
    def patch(self, request, pk):
        dashboard = self.get_object_by_pk(pk)

      
        serializer = DashboardSerializer(dashboard, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       

class DashboardApiDeleteView(BasicDashboardApi): 
    """Delete a dashboard view"""
    serializer_class = DashboardSerializer
    def delete(self, request, pk):
        dashboard = self.get_object_by_pk(pk)
      
    
        if dashboard and dashboard.user.id == request.user.id:
            dashboard.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
    

class TaskCategorieListApiView(BasicDashboardApi):
    serializer_class = TaskCategorieSerializer

    def get(self, request):
        categories = TaskCategorie.objects.all()
        serializer = TaskCategorieSerializer(categories, many=True)
        return Response(serializer.data)


class TaskCategorieCreateApiView(BasicDashboardApi):
    serializer_class = TaskCategorieSerializer

    def post(self, request):
        data = request.data
     

        serializer = TaskCategorieSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCategoriePatchApiView(BasicDashboardApi):
    serializer_class = TaskCategorieSerializer
    

    def patch(self, request, pk):
        category = self.get_category_object(pk)

      
        serializer = TaskCategorieSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TaskCategorieUpdateApiView(BasicDashboardApi):
    serializer_class = TaskCategorieSerializer
    

    def put(self, request, pk):
        category = self.get_category_object(pk)

      
        serializer = TaskCategorieSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCategorieDeleteApiView(BasicDashboardApi):
    """Delete a category view"""
    serializer_class = DashboardSerializer
    def delete(self, request, pk):
        category = self.get_category_object(pk)
        if category:
            category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)