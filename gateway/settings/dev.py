from .base import *

DEBUG = True

INSTALLED_APPS += (
    'debug_toolbar',
    'django_nose',
)

MIDDLEWARE += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-html',
    '--cover-erase',
    '--cover-package=core,payments',
]

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mailtrap.io')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER','1665e6379817b4fa')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD','2f1a896c9f2e6f')
EMAIL_PORT = os.environ.get('EMAIL_PORT','2525')

SITE_DOMAIN = 'http://localhost:8000'


