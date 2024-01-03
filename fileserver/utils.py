import mimetypes
import re
import unicodedata
import os

from functools import lru_cache
from urllib.parse import quote
from pathlib import _PosixFlavour, _WindowsFlavour
from pathlib import Path as PathOrigin
from pathlib import PurePath as PurePathOrigin
from django.http import Http404, HttpResponse, FileResponse

# from django.views.static import serve
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class PurePath(type(PurePathOrigin())):
    # for 'PurePath' has no '_flavour' member error
    _flavour = _PosixFlavour() if os.name == 'posix' else _WindowsFlavour()


class Path(type(PathOrigin())):
    # for 'PurePath' has no '_flavour' member error
    _flavour = _PosixFlavour() if os.name == 'posix' else _WindowsFlavour()


async def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    """iterate file chunk by chunk in generator mode"""
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


async def dev(request, filename, **kwargs):
    size = os.path.getsize(filename)

    response = FileResponse(
        file_iterator(
            filename,
            offset=0,
            length=size
        ),
        # status=206,
    )
    response['Content-length'] = size

    return response


async def nginx(request, filename, **kwargs):
    response = HttpResponse()
    response['X-Accel-Redirect'] = _convert_file_to_url(filename)

    return response


@lru_cache(maxsize=None)
def _get_sendfile():
    sendfile_backend = getattr(settings, 'SENDFILE_BACKEND', None)
    if sendfile_backend:
        return sendfile_backend

    if settings.IS_RUNSERVER:
        return dev

    return nginx


def _convert_file_to_url(path):
    try:
        url_root = PurePath(getattr(settings, "SENDFILE_URL", None))
    except TypeError:
        return path

    path_root = PurePath(settings.SENDFILE_ROOT)
    path_obj = PurePath(path)

    relpath = path_obj.relative_to(path_root)
    url = relpath._flavour.pathmod.normpath(str(url_root / relpath))

    return quote(str(url))


def _sanitize_path(filepath, root_path=None):

    if not root_path:
        try:
            path_root = Path(getattr(settings, 'SENDFILE_ROOT', None))
        except TypeError as e:
            raise ImproperlyConfigured('You must specify a value for SENDFILE_ROOT') from e
    else:
        path_root = Path(root_path)

    filepath_obj = Path(filepath)

    filepath_abs = Path(filepath_obj._flavour.pathmod.normpath(str(path_root / filepath_obj)))

    try:
        filepath_abs.relative_to(path_root)
    except ValueError as e:
        raise Http404(f'{filepath_abs} wrt {path_root} is impossible') from e

    return filepath_abs


async def sendfile(request, filename, attachment=False, attachment_filename=None,
                   mimetype=None, encoding=None, root_path=None):
    """
    Create a response to send file using backend configured in ``SENDFILE_BACKEND``

    ``filename`` is the absolute path to the file to send.

    If ``attachment`` is ``True`` the ``Content-Disposition`` header will be set accordingly.
    This will typically prompt the user to download the file, rather
    than view it. But even if ``False``, the user may still be prompted, depending
    on the browser capabilities and configuration.

    The ``Content-Disposition`` filename depends on the value of ``attachment_filename``:

        ``None`` (default): Same as ``filename``
        ``False``: No ``Content-Disposition`` filename
        ``String``: Value used as filename

    If neither ``mimetype`` or ``encoding`` are specified, then they will be guessed via the
    filename (using the standard Python mimetypes module)
    """
    filepath_obj = _sanitize_path(filename, root_path)
    _sendfile = _get_sendfile()

    if not filepath_obj.exists() or not filepath_obj.is_file():
        raise Http404(f'"{filename}" does not exist')

    content_type, guessed_encoding = mimetypes.guess_type(str(filepath_obj))

    if mimetype is None:
        if content_type:
            mimetype = content_type
        else:
            mimetype = 'application/octet-stream'

    response = await _sendfile(request, filepath_obj)

    # Suggest to view (inline) or download (attachment) the file
    parts = ['attachment' if attachment else 'inline']

    if attachment_filename is None:
        attachment_filename = filepath_obj.name

    if attachment_filename:
        attachment_filename = str(attachment_filename).replace("\\", "\\\\").replace('"', r"\"")
        ascii_filename = unicodedata.normalize('NFKD', attachment_filename)
        ascii_filename = ascii_filename.encode('ascii', 'ignore').decode()
        parts.append(f'filename="{ascii_filename}"')

        if ascii_filename != attachment_filename:
            quoted_filename = quote(attachment_filename)
            parts.append(f'filename*=UTF-8\'\'{quoted_filename}')

    response['Content-Disposition'] = '; '.join(parts)
    response['Content-Type'] = mimetype

    # response['Content-length'] = filepath_obj.stat().st_size
    response['Connection'] = "Keep-Alive"
    # response['Connection'] = "Keep-Alive"

    if not encoding:
        encoding = guessed_encoding

    if encoding:
        response['Content-Encoding'] = encoding

    return response
