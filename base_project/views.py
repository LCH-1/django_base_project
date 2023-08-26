from django.conf import settings
from fileserver.utils import sendfile


async def static_view(request, path, document_root=None, show_indexes=False):
    return await sendfile(request, path, root_path=settings.STATIC_ROOT)
