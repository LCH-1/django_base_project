import logging
import logging.handlers
import django
import rest_framework

from django.conf import settings

from rich import get_console
from rich.pretty import pretty_repr
from rich.logging import RichHandler
from rich.console import Console

DEFAULT_SETTING = {
    "level": logging.NOTSET,
    "show_time": False,
    "show_level": False,
    "show_path": False,
    "rich_tracebacks": True,
    "tracebacks_extra_lines": 5,
    "tracebacks_suppress": [django, rest_framework],
}
LOGFILE = settings.LOGFILE


class DefaultLogHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        kwargs.update(DEFAULT_SETTING)
        super().__init__(*args, **kwargs)


class NoOutputLogHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        kwargs.update(DEFAULT_SETTING)
        kwargs["console"] = Console(quiet=True)
        super().__init__(*args, **kwargs)


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            "filename": LOGFILE,
            "when": "midnight",
            "interval": 1,
            "backupCount": 10,
        })

        super().__init__(*args, **kwargs)


class LogFileHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        kwargs.update(DEFAULT_SETTING)
        kwargs["console"] = Console(file=open(LOGFILE, "a", encoding="utf-8"), width=150)
        super().__init__(*args, **kwargs)


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.manager = logging.Logger.manager
        logging.Logger.manager.loggerDict[name] = self

    def out(self, msg):
        return pretty_repr(msg, max_width=get_console().size.width, max_string=200)

    def debug(self, msg="", *args, **kwargs):
        return super().debug(self.out(msg), *args, **kwargs)

    def info(self, msg="", *args, **kwargs):
        return super().info(self.out(msg), *args, **kwargs)

    def warning(self, msg="", *args, **kwargs):
        return super().warning(self.out(msg), *args, **kwargs)

    def error(self, msg="", *args, **kwargs):
        return super().error(self.out(msg), *args, **kwargs)

    def findCaller(self, stack_info=False, stacklevel=1):
        # ????????? filename ????????? ?????? stacklevel??? 3?????? ??????
        return super().findCaller(stack_info, stacklevel=3)


class DefaultFormatter(logging.Formatter):
    def format(self, record):
        try:
            from .middleware import local
            request = getattr(local, 'django_request', None)
            record.userinfo = str(request.user)

        except:
            record.userinfo = '-'

        try:
            record.filepath = "/".join(record.pathname.rsplit("\\", 2)[1:])

        except:
            record.filepath = record.filename

        return super().format(record)


default_logger = CustomLogger("console_debug")
request_logger = CustomLogger("request_log")
