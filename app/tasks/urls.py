from django.urls import path, include
from . import views


app_name = 'tasks'
urlpatterns = [
    path("taskcomment-list/", views.TaskCommentListView.as_view(), name="taskcomment-list"),
    path("taskcomment-create/", views.TaskCommentCreateApiView.as_view(), name="taskcomment-create"),
    path("taskcomment-list/<int:pk>", views.TaskCommentListView.as_view(), name="taskcomment-list"),
    path("taskcomment-patch/<int:pk>", views.TaskCommentApiPatchView.as_view(), name="taskcomment-patch"),
    path("taskcomment-delete/<int:pk>", views.TaskCommentApiDeleteView.as_view(), name="taskcomment-delete"),
    path("task-create/", views.TaskApiCreateView.as_view(), name="task-create"),
    path("task-list/", views.TaskListView.as_view(), name="task-list"),
    path("task-detail/<uuid:pk>", views.TaskListView.as_view(), name="task-detail"),
    path("task-patch/<uuid:pk>", views.TaskApiPatchView.as_view(), name="task-patch"),
    path("task-update/<uuid:pk>", views.TaskApiUpdateView.as_view(), name="task-update"),
    path("task-delete/<uuid:pk>", views.TaskApiDeleteView.as_view(), name="task-delete"),
    path('task-upload-image/<uuid:pk>/upload-image/', views.TaskImageUploadView.as_view(), name='task-upload-image'),

]