# -*- coding: utf-8 -*-
# Django settings for site pyatt Django project.

import os, sys
from django.utils.translation import gettext_lazy as _

from main import constant
import logging

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(-1, PROJECT_PATH)
sys.path.insert(-1, "/home/vincent/Documents/donnees/DIVERS/DeveloppementLogiciel/python/MyPyTools")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bvmnzxbf8*l*m@5k7+f$71n@_*%8_u3)rj3j7rkac^ei@z6iy8'

ALLOWED_HOSTS = []


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

STATIC_URL = '/static/'
ROOT_URLCONF = 'main.urls'

MEDIA_ROOT = os.path.join(PROJECT_PATH, "main", "media")
MEDIA_URL = '/static/../media/' 

WSGI_APPLICATION = 'main.wsgi.application'

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "main"
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['main','templates'],
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

LANGUAGE_CODE = 'fr_fr'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = False

log = logging.getLogger(constant.APP_NAME)
## Create traces logger
s_format = '[%(asctime)s %(name)s_%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
## add file handler
logFile = os.path.abspath(os.path.join(PROJECT_PATH, constant.APP_NAME + ".log"))

hdlr = logging.FileHandler(logFile)
hdlr.setFormatter(logging.Formatter(s_format))
log.addHandler(hdlr)
## add stdout handler
hdlr = logging.StreamHandler()
hdlr.setFormatter(logging.Formatter(s_format))
log.addHandler(hdlr)    
log.setLevel(logging.INFO)

logging.getLogger('utils').setLevel(logging.INFO)