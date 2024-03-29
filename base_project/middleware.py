import time
import json
import threading

from django.conf import settings
from django.contrib.auth import get_user

from rest_framework.status import is_client_error, is_server_error

from base_project.logger import request_logger

MEDIA_URL = settings.MEDIA_URL
local = threading.local()


class RequestLogMiddleware:
    """Request / Response logging"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.response_log = None
        self.start_time = None

    def __call__(self, request):
        self.start_time = time.time()
        log_data = {
            "remote_address": request.META["REMOTE_ADDR"],
            "request_method": request.method,
            "request_path": request.get_full_path(),
            "content_type": request.content_type,
        }

        full_path = str(request.get_full_path())
        is_logging = bool(
            full_path.startswith("/api/") and
            MEDIA_URL not in full_path and
            "insomnia" not in (user_agent := request.headers.get("user_agent", "")) and
            "Postman" not in user_agent and
            (
                (refferer := request.META.get('HTTP_REFERER')) and
                "swagger" not in refferer and
                "redoc" not in refferer
            )
        )

        if is_logging:
            try:
                req_body = json.loads(request.body.decode("utf-8")) if request.body else {}
            except:
                try:
                    splited_request_body = request.body.split(b"\r")
                    req_body = []
                    for line in splited_request_body:
                        try:
                            decode_line = line.decode()
                        except:
                            pass

                        if "Content-Disposition" in decode_line:
                            req_body.append(decode_line.strip())
                except:
                    req_body = ["big size file uploaded"]

            log_data["request_body"] = req_body

        request_logger.debug(log_data)

        # after response
        response = self.get_response(request)

        self.response_log = {
            "status": response.status_code,
            "user_info": str(request.user),
        }

        if is_logging and not is_server_error(response.status_code):
            try:
                self.response_log["response_body"] = json.loads(response.content.decode())
            except:
                self.response_log["response_body"] = ""

        self.response_log["runtime"] = time.time() - self.start_time
        request_logger.debug(self.response_log, max_length=5)

        return response

    def process_response(self, request, response):
        return response


class LoggedInUserMiddleware:
    """user info를 logging 하기 위해 사용"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(local, 'django_request', request)
        return self.get_response(request)
