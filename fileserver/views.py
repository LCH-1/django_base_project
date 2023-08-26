
from django.http import JsonResponse

from rest_framework import status

from user.models import User
from fileserver.utils import sendfile

MODEL_MAPPING = {
    "user": User,
}

async def sendfile_view(request, filename):
    return await sendfile(request, filename)


async def protected_sendfile_view(request, model, field, pk):
    model = MODEL_MAPPING[model]
    obj = await model.objects.aget(pk=pk)
    permission_checker = getattr(obj, f"has_{field}_permission", None)

    if not permission_checker or not permission_checker(request.user):
        return JsonResponse({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    file_ = getattr(obj, field)

    return await sendfile(request, file_.path)
