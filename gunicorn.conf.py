import importlib
import multiprocessing

host = "0.0.0.0"
port = 8000

bind = f"{host}:{port}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "base_project.workers.UvicornWorker"
# preload_app = True
# reload = True
