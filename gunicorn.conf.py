import multiprocessing
from os import environ as env

from base_project.settings import PROJECT_NAME
from base_project import startup


# gunicorn으로 실행 시 초기 실행
def when_ready(server):
    startup.run()


host = env.get("GUNICORN_HOST", "0.0.0.0")
port = int(env.get("GUNICORN_PORT", 8000))

bind = f"{host}:{port}"
# threads = multiprocessing.cpu_count() * 2
workers = int(env.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

worker_class = f"{PROJECT_NAME}.workers.UvicornWorker"
# preload_app = True
# reload = True
