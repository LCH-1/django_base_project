from pathlib import Path
import os
import posixpath

from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils.http import http_date
from django.utils._os import safe_join

from fileserver.utils import sendfile


async def static_serve(request, path, insecure=False, **kwargs):
    normalized_path = posixpath.normpath(path).lstrip("/")
    absolute_path = finders.find(normalized_path)
    document_root, path = os.path.split(absolute_path)
    fullpath = Path(safe_join(document_root, path))
    statobj = fullpath.stat()

    response = await sendfile(request, path, root_path=document_root)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)

    return response


async def static_view(request, path, document_root=None, show_indexes=False):
    return await sendfile(request, path, root_path=settings.STATIC_ROOT)
