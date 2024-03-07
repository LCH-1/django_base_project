from pathlib import Path
import os
import posixpath

from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils.http import http_date
from django.utils._os import safe_join
from django.http.response import HttpResponseBadRequest
from django.core.exceptions import ValidationError

from rest_framework.views import exception_handler

from base_project.serializers import ValidationError
from fileserver.utils import sendfile


async def static_serve(request, path, insecure=False, **kwargs):
    """
    async용 static_server 함수 재정의
    """

    normalized_path = posixpath.normpath(path).lstrip("/")
    absolute_path = finders.find(normalized_path)
    if not absolute_path:
        return HttpResponseBadRequest(f"Invalid path: {path}")

    document_root, path = os.path.split(absolute_path)
    fullpath = Path(safe_join(document_root, path))
    statobj = fullpath.stat()

    response = await sendfile(request, path, root_path=document_root)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)

    return response


async def static_view(request, path, document_root=None, show_indexes=False):
    """
    async용 static_view 함수 재정의
    """
    return await sendfile(request, path, root_path=settings.STATIC_ROOT)


def list_to_string_exception_handler(exc, context):
    """
    list 형태의 exception info를 string으로 변환
    """

    response = exception_handler(exc, context)
    if isinstance(exc, ValidationError) and isinstance(exc.detail, dict):
        data = {}
        for key, value in exc.detail.items():
            if isinstance(value, list):
                value_ = value[0]
            else:
                value_ = value

            if value_ == "True":
                value_ = True
            elif value_ == "False":
                value_ = False

            data[key] = value_

        response.data = data

    return response
