from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from account.models import User
from account.serializers import UserSerializer
from base_project.pagination import get_pagination_class, PageNumberPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = get_pagination_class(5)
