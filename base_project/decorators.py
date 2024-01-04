from functools import wraps
import json

from django.core.cache import cache

from rest_framework.response import Response

from acs.utils import get_cached_list


def caching_view(caching_request_data=True, alias=None):
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
                view_info = f"{module_path}.{class_name}.{function_name}"

            if caching_request_data:
                params_string = str(request.GET.dict()).replace(" ", "")
                cache_key = f"{view_info}-{params_string}"

            else:
                cache_key = view_info

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
