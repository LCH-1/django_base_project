from rest_framework.permissions import AllowAny

from base_project import viewsets
from base_project.pagination import get_pagination_class, PageNumberPagination

from user.models import User
from user.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = get_pagination_class(5)
