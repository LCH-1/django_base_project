import importlib
import multiprocessing

from manage import SETTINGS_PATH

settings = importlib.import_module(SETTINGS_PATH)

host = "0.0.0.0"
port = 8000

bind = f"{host}:{port}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = f"{settings.PROJECT_NAME}.workers.UvicornWorker"
# preload_app = True
# reload = True
