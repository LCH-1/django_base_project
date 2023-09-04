import multiprocessing

host = "0.0.0.0"
port = 8000
wsgi_app = "base_project.asgi:application"

bind = f"{host}:{port}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "base_project.workers.UvicornWorker"
# preload_app = True
# reload = True
