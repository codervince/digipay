import os
from .base import *

DEBUG = False

# TODO
# ALLOWED_HOSTS = [
# ]

RAVEN_CONFIG = {
    'dsn': os.environ['DSN'],
}

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

