import mimetypes

from django.http import JsonResponse
from django.http import Http404
from django.core.cache import cache

from rest_framework import status

from base_project import models
from base_project.logger import logger

from fileserver.utils import sendfile

MODEL_MAPPING = {
}

PERMISSION_DENIED_RESPONSE = JsonResponse(
    {"error": "Media file does not exist or permission denied"},
    status=status.HTTP_403_FORBIDDEN
)


async def sendfile_view(request, filename):
    if filename.endswith("/"):
        filename = filename[:-1]

    return await sendfile(request, filename)


async def protected_sendfile_view(request, model_, field, pk):
    try:
        model = MODEL_MAPPING[model_]
        obj = await model.objects.aget(pk=pk)
    except models.DoesNotExist:
        return PERMISSION_DENIED_RESPONSE

    permission_checker = getattr(obj, f"has_{field}_permission", None)

    if not permission_checker or not await permission_checker(request):
        return PERMISSION_DENIED_RESPONSE

    file_ = getattr(obj, field)

    return await sendfile(request, file_.path)
