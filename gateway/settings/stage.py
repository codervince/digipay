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

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.getenv('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
