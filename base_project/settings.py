import os
import sys
from pathlib import Path
from django.db.models import Field

IS_RUNSERVER = 'runserver' in sys.argv or sys.argv[0].rsplit("\\", maxsplit=1)[-1] == 'uvicorn'

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
PROJECT_NAME = os.path.basename(PROJECT_ROOT)

# db unique intergrity validation 메세지 변경
Field.default_error_messages.update({
    "unique": "이미 존재하는 %(field_label)s입니다.",
})

SECRET_KEY = os.environ.get('SECRET_KEY', ' ')

DEBUG = os.environ.get('DEBUG', '1') == '1'

if DEBUG:
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", ]

else:
    ALLOWED_HOSTS = ['']
    CSRF_TRUSTED_ORIGINS = []

CORS_ORIGIN_WHITELIST = CSRF_TRUSTED_ORIGINS

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # libraries
    'django_cleanup.apps.CleanupConfig',  # filefield가 update 될 때 기존 파일 삭제
    'rest_framework',
    'ckeditor',

    # apps
    'user',
    'fileserver',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        f'{PROJECT_NAME}.permissions.IsAuthenticated'
    ],

    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    # 'PAGE_SIZE': 10,
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'
    INSTALLED_APPS += [
        'drf_spectacular_sidecar',
        'drf_spectacular',
    ]
    SPECTACULAR_SETTINGS = {
        'SWAGGER_UI_DIST': 'SIDECAR',
        'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
        'REDOC_DIST': 'SIDECAR',
    }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    f'{PROJECT_NAME}.middleware.LoggedInUserMiddleware',  # logger formatter에서 request를 받아오기 위해 사용
]

if DEBUG:
    MIDDLEWARE.append(f'{PROJECT_NAME}.middleware.RequestLogMiddleware')

MIDDLEWARE.append(f'{PROJECT_NAME}.middleware.ResponseFormattingMiddleware')

ROOT_URLCONF = f'{PROJECT_NAME}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = f'{PROJECT_NAME}.wsgi.application'


# Database
# 환경변수에 POSTGRESQL_DB가 있을 경우 postgres에 연결 시도
if POSTGRES_DB := os.environ.get('POSTGRES_DB', ''):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': POSTGRES_DB,
            'USER': os.environ.get('POSTGRES_USER', ''),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', ''),
            'PORT': os.environ.get('POSTGRES_PORT', ''),
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "user.User"

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True
USE_L10N = True

USE_TZ = False  # timezone을 사용하지 않음

MEDIA_URL = 'api/fileserver/'
MEDIA_DIR = 'media'
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_DIR)

""" sendfile start """
# SENDFILE_BACKEND = ''
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/protected'
""" sendfile end """

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = '/admin/login/'

LOGFILE = 'general.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    'formatters': {
        'debug_console': {
            '()': f'{PROJECT_NAME}.logger.DefaultFormatter',
            'format': '[{filepath}:{lineno}] | {userinfo} >> {message}',
            'style': '{',
        },
        'console': {
            '()': f'{PROJECT_NAME}.logger.DefaultFormatter',
            'format': '[{asctime}.{msecs:03.0f}] {message} | {userinfo}',
            # 'format': '[{asctime}.{msecs:03.0f}] {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{message}',
            'style': '{',
            'datefmt': '-',
        },
        'file': {
            '()': f'{PROJECT_NAME}.logger.DefaultFormatter',
            'format': '[{asctime}] | {levelname:7} | [{filepath}:{funcName}:{lineno}] | {userinfo} | >> {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': f'{PROJECT_NAME}.logger.DefaultLogHandler',
            'formatter': 'console',
            'level': 'DEBUG',
        },
        'no_output_console': {
            'class': f'{PROJECT_NAME}.logger.NoOutputLogHandler',
            'formatter': 'console',
        },
        'debug_console': {
            'class': f'{PROJECT_NAME}.logger.DefaultLogHandler',
            'formatter': 'debug_console',
            'level': 'DEBUG',
        },
        'request_log': {
            'class': f'{PROJECT_NAME}.logger.DefaultLogHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
        'sql_query': {
            'class': f'{PROJECT_NAME}.logger.DefaultLogHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
        'file': {
            # django를 runserver로 실행시켰을 때는 LogFileHandler 사용
            'class': f'{PROJECT_NAME}.logger.{"LogFileHandler" if IS_RUNSERVER else "TimedRotatingFileHandler"}',
            'formatter': 'file',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        # default disable
        'django': {
            'handlers': ['no_output_console']
        },

        'django.server': {
            'handlers': ['console', 'file'],
        },

        'django.request': {
            'handlers': ['console', 'file'],
        },

        # logger.debug() log
        'console_debug': {
            'level': 'DEBUG',
            "filters": ["require_debug_true"],
            'handlers': ['debug_console', 'file'],
        },

        # middleware request log
        'request_log': {
            'level': 'DEBUG',
            "filters": ["require_debug_true"],
            'handlers': ['request_log', 'file'],
        },

        # database query log
        # 'django.db.backends': {
        #     'handlers': ['sql_query', ],
        #     'level': 'DEBUG',
        # },
    },
}
