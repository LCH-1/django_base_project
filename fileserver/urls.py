from django.urls import path, re_path, include

from rest_framework.routers import DefaultRouter

from fileserver import views

urlpatterns = [
    re_path(r'^protected/(?P<model>\w+)/(?P<field>\w+)/(?P<pk>\w+)/?$', views.protected_sendfile_view),
    re_path(r'^(?!protected/)(?P<filename>[ㄱ-ㅎ가-힣()\w\s.,-/]+)$', views.sendfile_view),
]
