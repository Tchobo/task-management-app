from django.urls import path, include
from . import views


app_name = 'dashboard'
urlpatterns = [
    path("dashboard-list/", views.DashboardApiListView.as_view(), name="dashboard-list"),
    path("dashboard-list/<uuid:slug>", views.DashboardApiListView.as_view(), name="dashboard-list"),
    path("dashboard-create/", views.DashboardApiCreateView.as_view(), name="dashboard-create"),
    path("dashboard-delete/<int:pk>", views.DashboardApiDeleteView.as_view(), name="dashboard-delete"),
    path("dashboard-update/<int:pk>", views.DashboardApiUpdateView.as_view(), name="dashboard-update"),
    path("dashboard-patch/<int:pk>", views.DashboardApiPatchView.as_view(), name="dashboard-patch"),
    path("category-list", views.TaskCategorieListApiView.as_view(), name="category-list"),
    path("category-create", views.TaskCategorieCreateApiView.as_view(), name="category-create"),
    path("category-patch/<int:pk>", views.TaskCategoriePatchApiView.as_view(), name="category-patch"),
    path("category-update/<int:pk>", views.TaskCategorieUpdateApiView.as_view(), name="category-update"),
    path("category-delete/<int:pk>", views.TaskCategorieDeleteApiView.as_view(), name="category-delete"),

]