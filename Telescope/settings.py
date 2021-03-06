"""
Django settings for Telescope project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from mongoengine import connect
import djcelery
import HouseHealth.constants as const
djcelery.setup_loader()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^)m*&gge2!+2bbral&2-(eqch&vm-vjurp+@^0w+_lo)mc*nq^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'check_auth'

SOCIAL_AUTH_GITHUB_KEY = 'c3521a2beaf4051aee8d'
SOCIAL_AUTH_GITHUB_SECRET = '4ef1f53b7a45ab3f2e14d622b6ae9e92c9822f89'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY ='792404492852-0ujobvpm48lic6gqjvpfjg048l7q3lkl.apps.googleusercontent.com'  #Paste CLient Key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'N9aVD56cctn0Q7rbFlsyRzvm' #Paste Secret Key

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'HouseHealth.apps.HousehealthConfig',
    'djcelery',
    'social_django',
    'lense',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'Telescope.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  # <--
                'social_django.context_processors.login_redirect', # <--
            ],
        },
    },
]

WSGI_APPLICATION = 'Telescope.wsgi.application'

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_IMPORTS = ('HouseHealth.tasks',)
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
connect('mongodbtut', host='127.0.0.1', port=27017)


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
'social_core.backends.open_id.OpenIdAuth',  # for Google authentication
 'social_core.backends.google.GoogleOpenId',  # for Google authentication
 'social_core.backends.google.GoogleOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

log_file = BASE_DIR + '/logs/telescope_application.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s]: {Time: %(asctime)s, File: %(filename)s, '
                        'Function: %(funcName)s, Module: %(module)s, Message: %(message)s}'
        },
        'simple': {
            'format': '%(levelname)s [Time: %(asctime)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': const.LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': const.LOG_LEVEL,
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'backupCount': 10,
            'filename': log_file,
            'formatter': 'verbose'
        },
        'gelf': {
            'level': const.LOG_LEVEL,
            'class': 'graypy.GELFHandler',
            'host': const.LOG_URL,
            'port': const.LOG_PORT
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': const.LOG_LEVEL,
            'propagate': False,
        },
        'gelf_django': {
            'handlers': ['file', 'console', 'gelf'],
            'level': const.LOG_LEVEL,
            'propagate': False,
        }
    }
}

from LogEndPoint.dyfo_logger import set_logger_dict, getLogger
set_logger_dict(LOGGING)
logger = getLogger('django', 'TELESCOPE')
