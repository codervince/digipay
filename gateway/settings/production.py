import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['138.68.90.116']

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
DEFAULT_FROM_EMAIL = os.getenv('APP_ADMIN_EMAIL')

# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# CSRF_TRUSTED_ORIGINS = ['yourgateway.com']
# # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_HSTS_SECONDS = 3600
