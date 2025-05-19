"""Django settings for IDTrackrBackend project."""

import logging.config
import os

from id_tracker.config.utilities import get_bool_env

ENVIRONMENT = os.getenv("ENVIRONMENT", "test").lower()
DEBUG = get_bool_env("DEBUG")
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "corsheaders",
]

LOCAL_APPS = [
    "id_tracker",
]

INSTALLED_APPS += LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", False)

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# frontend origin
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]


ROOT_URLCONF = "id_tracker.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "id_tracker.config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "idtrackr_db"),
        "USER": os.getenv("DB_USER", "app"),
        "PASSWORD": os.getenv("DB_PASSWORD", "app"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa
    },
]

# Locale settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = (
    # SMTP server address
    "smtp.gmail.com"
)
# SMTP server configuration
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "mikemaximus132015@gmail.com"
EMAIL_HOST_PASSWORD = "ddvn pien pfxo ysso"

# Logging settings
""" Logging """
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] "
            + "%(module)s %(process)d %(thread)d %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": False,
            "level": "INFO" if DEBUG else "ERROR",
            "name": ENVIRONMENT,
        },
        "django.request": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO" if DEBUG else "ERROR",
            "name": ENVIRONMENT,
            "filters": ["require_debug_false"],
        },
        "django.db": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO" if DEBUG else "ERROR",
            "name": ENVIRONMENT,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO" if DEBUG else "ERROR",
            "name": ENVIRONMENT,
        },
        "id_tracker": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
            "name": ENVIRONMENT,
        },
        "": {
            "handlers": ["console"],
            "level": "INFO" if DEBUG else "ERROR",
            "name": ENVIRONMENT,
            "propagate": False,
        },
    },
}
LOGGING_CONFIG = None
logging.config.dictConfig(LOGGING)
