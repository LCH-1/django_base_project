import os

import django
from django.conf import settings

from base_project.logger import logger
from django.conf import settings
from django.db import connections
from django.core.cache import caches
from django.core.cache.backends.base import BaseCache
from django.db.utils import OperationalError


def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_project.settings')
    django.setup(set_prefix=False)
    if settings.DEBUG:
        logger.debug("################################################")
        logger.debug("################################################")
        logger.debug("################################################")
        logger.debug("############# DEBUG MODE ENABLED!! #############")
        logger.debug("################################################")
        logger.debug("################################################")
        logger.debug("################################################")

    logger.warning(f"log file location : {settings.LOGFILE}")
    logger.warning(f"local mode : {settings.IS_LOCAL}")
    logger.info("@@ Database Connection Status @@")
    for db_name in settings.DATABASES:
        connection = connections[db_name]
        try:
            connection.ensure_connection()
            logger.warning(f"Connected to {db_name} DB")
        except OperationalError:
            logger.warning(f"Failed to connect to {db_name} DB")

        db_engine = settings.DATABASES[db_name]['ENGINE'].replace('django.db.backends.', '')
        logger.warning("###### DB INFO ######")
        logger.warning(f"ENGINE : {db_engine}")
        logger.warning(f"NAME   : {settings.DATABASES[db_name]['NAME']}")
        logger.warning(f"HOST   : {settings.DATABASES[db_name]['HOST']}")
        logger.warning("#####################")

    logger.info("")
    logger.info("@@ Cache Connection Status @@")
    for cache_name in settings.CACHES:
        cache = caches[cache_name]
        try:
            cache.set('test_key', 'test_value', timeout=30)
            if cache.get('test_key') == 'test_value':
                logger.warning(f"Connected to {cache_name} cache")
            else:
                logger.warning(f"Connection to {cache_name} cache failed")
        except:
            logger.warning(f"Connection to {cache_name} cache failed")
        cache_backend = settings.CACHES[cache_name]['BACKEND'].replace('django.core.cache.backends.', '')
        logger.warning("##### CACHE INFO ####")
        logger.warning(f"BACKEND : {cache_backend}")
        logger.warning("#####################")

    cache.clear()
