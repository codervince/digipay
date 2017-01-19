import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    # 'gateway.morethansoft.com'
    '*'
]

RAVEN_CONFIG = {
    'dsn': os.environ['DSN'],
}

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)
