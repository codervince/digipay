from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from raven import Client
from raven.contrib.celery import register_signal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings.dev')


if hasattr(settings, 'RAVEN_CONFIG'):
    client = Client(dsn=settings.RAVEN_CONFIG['dsn'])
    register_signal(client)


app = Celery('gateway', backend='redis://localhost')
app.config_from_object('django.conf:settings')
app.conf.beat_schedule = {
    # Every 2 minutes
    'check_transactions': {
        'task': 'api.tasks.check_transactions',
        'schedule': crontab(),
        # 'args': None,
    },
}

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
TASK_SERIALIZER = 'json'
ACCEPT_CONTENT = ['json']
