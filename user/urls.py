from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from user import views
from base_project.routers import UserRouter

custom_router = UserRouter()
custom_router.include_root_view = False
custom_router.register('', views.UserViewSet, basename="user")

urlpatterns = [
    path('', include(custom_router.urls)),
]
