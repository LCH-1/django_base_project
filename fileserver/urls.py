from django.contrib import admin
from django.urls import path, re_path, include

from rest_framework.routers import DefaultRouter

from fileserver import views

urlpatterns = [
    path('protected/<str:model>/<str:field>/<str:pk>', views.protected_sendfile_view),
    re_path(r'^(?P<filename>[ㄱ-ㅎ가-힣()\w\s.,-/]+)$', views.sendfile_view),
]
