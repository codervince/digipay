# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-11 00:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_sent',
            field=models.BooleanField(default=False),
        ),
    ]
