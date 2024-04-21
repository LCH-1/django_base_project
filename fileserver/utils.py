import mimetypes
import re
import unicodedata
import os
import aiofiles

from functools import lru_cache
from urllib.parse import quote
from pathlib import _PosixFlavour, _WindowsFlavour
from pathlib import Path as PathOrigin
from pathlib import PurePath as PurePathOrigin
from django.http import Http404, HttpResponse, FileResponse, StreamingHttpResponse

# from django.views.static import serve
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

MAX_LOAD_VOLUME = settings.STREAM_MAX_LOAD_VOLUME
RANGE_RE = re.compile(settings.STREAM_RANGE_HEADER_REGEX_PATTERN, re.I)


class PurePath(type(PurePathOrigin())):
    # for 'PurePath' has no '_flavour' member error
    _flavour = _PosixFlavour() if os.name == 'posix' else _WindowsFlavour()


class Path(type(PathOrigin())):
    # for 'PurePath' has no '_flavour' member error
    _flavour = _PosixFlavour() if os.name == 'posix' else _WindowsFlavour()


async def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    """iterate file chunk by chunk in generator mode"""
    async with aiofiles.open(file_name, "rb") as f:
        await f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = await f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


async def dev(request, filename, offset=0, size=None, status=200, **kwargs):
    if not size:
        size = os.path.getsize(filename)

    response = FileResponse(
        file_iterator(
            filename,
            offset=offset,
            length=size
        ),
        status=status,
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

    if not filepath_obj.exists() or not filepath_obj.is_file():
        raise Http404(f'"{filename}" does not exist')

    content_type, guessed_encoding = mimetypes.guess_type(str(filepath_obj))

    if content_type and content_type.startswith("video"):
        return await get_streaming_response(request, str(filepath_obj), filepath_obj, content_type)

    _sendfile = _get_sendfile()

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

    if not encoding:
        encoding = guessed_encoding

    if encoding:
        response['Content-Encoding'] = encoding

    return response


def get_first_byte(request):
    range_header = request.META.get('HTTP_RANGE', '').strip()
    if not range_header:
        return 0

    range_match = RANGE_RE.match(range_header)
    if range_match:
        first_byte, _ = range_match.groups()
        return int(first_byte) if first_byte else 0

    return 0


def get_last_byte(first_byte, size):
    last_byte = first_byte + 1024 * 1024 * MAX_LOAD_VOLUME

    if last_byte >= size:
        last_byte = size - 1

    return last_byte


def get_size(filename):
    return os.path.getsize(filename)


async def get_streaming_response(request, filename, filepath_obj, content_type,
                                 first_byte=None, last_byte=None, size=None):
    if not size:
        size = get_size(filename)

    if not first_byte:
        first_byte = get_first_byte(request)

    if not last_byte:
        last_byte = get_last_byte(first_byte, size)

    length = last_byte - first_byte + 1

    _sendfile = _get_sendfile()
    response = await _sendfile(
        request=request,
        filename=filename,
        status=206,
        offset=first_byte,
        size=length,
    )

    response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
    response['Content-Type'] = content_type
    response['Connection'] = "Keep-Alive"

    response['X-Accel-Buffering'] = 'no'
    response['Accept-Ranges'] = response['Content-Range']

    return response
