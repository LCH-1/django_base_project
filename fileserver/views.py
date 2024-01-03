
from django.http import JsonResponse

from rest_framework import status

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


async def protected_sendfile_view(request, model, field, pk):
    try:
        model = MODEL_MAPPING[model]
        obj = await model.objects.aget(pk=pk)
    except:
        return PERMISSION_DENIED_RESPONSE

    permission_checker = getattr(obj, f"has_{field}_permission", None)

    if not permission_checker or not await permission_checker(request):
        return PERMISSION_DENIED_RESPONSE

    file_ = getattr(obj, field)

    return await sendfile(request, file_.path)
