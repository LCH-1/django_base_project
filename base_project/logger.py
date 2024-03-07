import os
import asgiref
import logging
import logging.handlers

from rich import get_console
from rich.pretty import pretty_repr, pprint
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from rich.highlighter import NullHighlighter

import django
from django.conf import settings
from django.core.management.color import color_style

import rest_framework

DEFAULT_SETTING = {
    "level": logging.NOTSET,
    "show_time": False,
    "show_level": False,
    "show_path": False,
    "rich_tracebacks": True,
    "tracebacks_extra_lines": 5,
    "tracebacks_suppress": [django, rest_framework, asgiref],
}


class DefaultLogHandler(RichHandler):
    """ 기본적으로 사용되는 핸들러 """

    def __init__(self, *args, **kwargs):
        kwargs.update(DEFAULT_SETTING)
        super().__init__(*args, **kwargs)


class ConsoleLogHandler(RichHandler):
    """ 콘솔에 로그를 출력하는 핸들러 """

    def __init__(self, *args, **kwargs):
        kwargs.update(DEFAULT_SETTING)
        kwargs["highlighter"] = NullHighlighter()
        super().__init__(*args, **kwargs)


class NoOutputLogHandler(RichHandler):
    """ 로그를 출력하지 않는 핸들러 """

    def __init__(self, *args, **kwargs):
        kwargs.update(DEFAULT_SETTING)
        kwargs["console"] = Console(quiet=True)
        super().__init__(*args, **kwargs)


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """ 로그 파일을 날짜별로 생성하는 핸들러 """

    def __init__(self, *args, **kwargs):
        path, _ = os.path.split(settings.LOGFILE)
        if path:
            os.path.isdir(path) or os.makedirs(path)

        kwargs.update({
            "filename": settings.LOGFILE,
            "when": "midnight",
            "interval": 1,
            "backupCount": 10,
        })

        super().__init__(*args, **kwargs)


class LogFileHandler(RichHandler):
    """ 파일에 로그를 출력하는 핸들러 """

    def __init__(self, *args, **kwargs):
        path, _ = os.path.split(settings.LOGFILE)
        if path:
            os.path.isdir(path) or os.makedirs(path)

        kwargs.update(DEFAULT_SETTING)
        kwargs["console"] = Console(file=open(settings.LOGFILE, "a", encoding="utf-8"), width=150)
        super().__init__(*args, **kwargs)


class CustomLogger(logging.Logger):
    """ 로그를 로그 출력 시 pretty format 적용 """

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.manager = logging.Logger.manager
        logging.Logger.manager.loggerDict[name] = self

    def out(self, msg, max_string, max_length):
        return pretty_repr(msg, max_width=get_console().size.width, max_string=max_string, max_length=max_length).strip(" '\"")

    def debug(self, msg="",  *args, max_string=200, max_length=None, **kwargs):
        super().debug(self.out(msg, max_string=max_string, max_length=max_length), *args, **kwargs)

    def info(self, msg="",  *args, max_string=200, max_length=None, **kwargs):
        super().info(self.out(msg, max_string=max_string, max_length=max_length), *args, **kwargs)

    def warning(self, msg="",  *args, max_string=200, max_length=None, **kwargs):
        super().warning(self.out(msg, max_string=max_string, max_length=max_length), *args, **kwargs)

    def error(self, msg="",  *args, max_string=200, max_length=None, **kwargs):
        super().error(self.out(msg, max_string=max_string, max_length=max_length), *args, **kwargs)

    def critical(self, msg="",  *args, max_string=200, max_length=None, **kwargs):
        super().critical(self.out(msg, max_string=max_string, max_length=max_length), *args, **kwargs)

    def exception(self, e):
        self.error("Exception occurred in try / except!")
        self.error(e, exc_info=True, stack_info=True)
        self.error("End of exception info, code is steel running")

    def findCaller(self, stack_info=False, stacklevel=1):
        # 정확한 filename 추적을 위해 stacklevel 수정
        if settings.IS_LOCAL:
            return super().findCaller(stack_info, stacklevel=3)

        return super().findCaller(stack_info, stacklevel=4)


class DefaultFormatter(logging.Formatter):
    """ logging에 user 정보를 추가하는 formatter """

    def set_record(self, record):
        try:
            from .middleware import local
            request = getattr(local, 'django_request', None)
            record.userinfo = str(request.user)

        except:
            record.userinfo = '-'

        try:
            record.filepath = "/".join(record.pathname.replace("\\", "/").rsplit("/", 2)[1:])

        except:
            record.filepath = record.filename

        if settings.IS_LOCAL:
            record.levelname_summary = record.levelname[0]

    def format(self, record):
        self.set_record(record)
        return super().format(record)


class ConsoleFormatter(DefaultFormatter):
    """ console에 출력하는 log의 lolor style 설정 """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = self.configure_style(color_style())

    def configure_style(self, style):
        style.DEBUG = style.HTTP_NOT_MODIFIED
        style.INFO = style.HTTP_INFO
        style.WARNING = style.HTTP_NOT_FOUND
        style.ERROR = style.ERROR
        style.CRITICAL = style.HTTP_SERVER_ERROR
        return style

    def colorizer(self, record):
        message = logging.Formatter.format(self, record)
        colorizer = getattr(self.style, record.levelname, self.style.HTTP_SUCCESS)
        return colorizer(message)

    def format(self, record):
        self.set_record(record)
        if (record.exc_info
                or record.exc_text
                or record.stack_info):
            return super().format(record)

        return self.colorizer(record)


logger = CustomLogger("console_debug")
silence_logger = CustomLogger("no_output_console")
request_logger = CustomLogger("request_log")
