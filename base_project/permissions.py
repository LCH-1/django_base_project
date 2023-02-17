from rest_framework.permissions import BasePermission as DjangoBasePermission
from rest_framework.exceptions import APIException
from rest_framework import status


class GenericAPIException(APIException):
    def __init__(self, status_code, detail=None, code=None):
        self.status_code = status_code
        super().__init__(detail=detail, code=code)


class BasePermission(DjangoBasePermission):
    message = '접근 권한이 없습니다.'


def check_login(*args, **kwargs):
    def decorator(func):
        def wrapper(self, request, view):
            # 사용자 login 체크
            if request.method in safe_methods or \
               request.user and request.user.is_authenticated:
                return func(self, request, view)

            raise GenericAPIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "서비스를 이용하기 위해 로그인 해주세요."}
            )

        return wrapper

    safe_methods = kwargs.get('safe_methods', [])

    # @decorator와 #decorator() 형태로 모두 사용할 수 있도록 함
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        return decorator(args[0])

    return decorator


class IsAuthenticated(BasePermission):
    '''로그인 한 사용자만 사용 가능'''
    @check_login
    def has_permission(self, request, view):
        return True


class IsAuthenticatedOrCreateOnly(BasePermission):
    '''로그인 한 사용자가 아니라면 생성만 가능'''

    @check_login(safe_methods=['POST'])
    def has_permission(self, request, view):
        return True


class IsAdminUser(BasePermission):
    '''admin 사용자만 접근 가능'''

    @check_login
    def has_permission(self, request, view):
        return bool(request.user.is_staff)
