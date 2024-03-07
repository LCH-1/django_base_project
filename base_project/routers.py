from rest_framework.routers import Route, DynamicRoute, DefaultRouter


class UserRouter(DefaultRouter):
    """
    UserViewSet을 위한 router
    사용자 정보(retrieve) 조회 시 request.user를 사용, pk 불필요
    """
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'create',
                'put': 'update',
                'delete': 'destroy'
            },
            name='{basename}-api',
            detail=False,
            initkwargs={}
        ),
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]


class CustomActionUrlRouter(DefaultRouter):
    """
    action(detail=True)로 설정 시 url 구조 변경
    기본 url 구조
        - ${pk}/${action_url}/
    수정된 url 구조
        - ${action_url}/${pk(optional)}/
    """
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),

        DynamicRoute(
            url=r'^{prefix}/{url_path}/?(?P<pk>[^/.]+)?{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]
