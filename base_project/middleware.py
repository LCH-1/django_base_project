import time
import json
import threading

from django.conf import settings
from django.contrib.auth import get_user

from rest_framework.status import is_client_error, is_server_error

from .logger import request_logger as logger


MEDIA_URL = settings.MEDIA_URL
local = threading.local()


class RequestLogMiddleware:
    """Request / Response Logging"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.response_log = None
        self.start_time = None

    def __call__(self, request):
        self.start_time = time.time()
        log_data = {
            "remote_address": request.META["REMOTE_ADDR"],
            "request_method": request.method,
            "content_type": request.content_type,
            "request_path": request.get_full_path(),
            "user_info": str(request.user),
        }

        full_path = str(request.get_full_path())
        is_logging = bool(
            "/api/" in full_path
            and MEDIA_URL not in full_path
            and "insomnia" not in request.headers.get("user_agent", "")
            and "Postman" not in request.headers.get("user_agent", "")
        )

        if is_logging:
            try:
                req_body = json.loads(request.body.decode("utf-8")) if request.body else {}
                for k in req_body:
                    if "password" in k:
                        req_body[k] = "#### Password ####"
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

            logger.debug(log_data)

        # after response
        response = self.get_response(request)
        if not is_logging or is_server_error(response.status_code):
            return response

        try:
            response_body = json.loads(response.content.decode())
        except:
            response_body = ""

        self.response_log = {
            "response_body": response_body,
            "status": response.status_code,
            "runtime": time.time() - self.start_time,
        }
        logger.debug(self.response_log)

        return response

    def process_response(self, request, response):
        return response


class ResponseFormattingMiddleware:
    """client error 통일"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not is_client_error(response.status_code) or not hasattr(response, "data"):
            return response

        if "insomnia" in request.headers.get("user_agent", "") or \
           "Postman" in request.headers.get("user_agent", ""):
            response_data = self.get_api_client_response(response)

        else:
            response_data = self.get_process_response(response)

        response.data = response_data
        response.content = response.render().rendered_content
        return response

    def get_process_response(self, response):
        """
        drf에서 로그를 2개 이상 리턴 해 줄 경우 1개만 출력하도록 수정
        log key "error"로 통일
        """
        data = response.data
        data_key = ''

        if isinstance(data, list) and len(data) >= 2:
            data = [max(data, key=len)]

        while not isinstance(data, str):

            if not data:
                break

            if isinstance(data, list):
                data = [x for x in data if x]
                data = data[0]
                if data == "이 필드는 필수 항목입니다.":
                    data = f"{data_key}는 필수 항목입니다."

            else:
                for k, v in data.items():
                    data_key = k
                    data = v
                    break

        return {"error": data}

    def get_api_client_response(self, response):
        return {
            "origin": response.data,
            "processed_response": self.get_process_response(response)
        }


class LoggedInUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(local, 'django_request', request)
        return self.get_response(request)
