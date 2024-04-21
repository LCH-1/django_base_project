from functools import wraps
import json

from django.core.cache import cache

from rest_framework.response import Response

from base_project.utils import get_cached_list


def caching_model_method(by_instance=True, by_user=True, using_cache_list=False):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(instance, request=None):
            model = instance.__class__.__name__
            method = view_func.__name__

            cache_key = f"{model}:{method}"
            if by_instance:
                cache_key += f":{instance.pk}"

            if by_user and request:
                if not request.user or not request.user.is_authenticated:
                    user = "anonymous"
                else:
                    user = request.user.pk

                cache_key += f":{user}"

            cached_data = cache.get(cache_key)

            if cached_data != None:
                return cached_data

            result = view_func(instance, request)

            cache.set(cache_key, result)

            if using_cache_list:
                cache_list_key = f"{model}:{method}:list"
                cache_list = cache.get(cache_list_key, [])
                cache_list.append(cache_key)
                cache.set(cache_list_key, cache_list)

            return result

        return _wrapped_view
    return decorator


def caching_view(caching_request_data=True, by_user=True, alias=None):
    """
    view에 들어오는 동일한 요청에 대해 응답을 캐싱하는 데코레이터

    Args:
        caching_request_data (bool, optional): request.GET의 parameter를 캐싱 키에 포함할지 여부. Defaults to True.
        alias (str, optional): 캐싱 키를 직접 지정할 경우 사용. Defaults to None.

    Example:
        class UserViewSet(viewsets.ModelViewSet):
            ...
            @caching_view(alias="${some alias}", caching_request_data=False)
            @action(detail=False, methods=["GET"])
            def some_function(self, request):
                ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            if request.method != "GET":
                return view_func(instance, request, *args, **kwargs)

            if alias:
                view_info = alias

            else:
                class_ = instance.__class__
                module_path = class_.__module__
                class_name = class_.__name__
                function_name = view_func.__name__
                view_info = f"{module_path}:{class_name}:{function_name}"

            if caching_request_data:
                params_string = str(request.GET.dict()).replace(" ", "")
                cache_key = f"{view_info}:{params_string}"

            else:
                cache_key = view_info

            if by_user:
                if not request.user or not request.user.is_authenticated:
                    user = "anonymous"
                else:
                    user = request.user.pk

                cache_key += f":{user}"

            cached_data = cache.get(cache_key)

            if cached_data != None:
                return Response(cached_data)

            response = view_func(instance, request, *args, **kwargs)
            cache.set(cache_key, response.data)
            cached_list_key, cached_list = get_cached_list(view_info)
            cached_list.append(cache_key)
            cache.set(cached_list_key, json.dumps(cached_list))

            return response

        return _wrapped_view
    return decorator
