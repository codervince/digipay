# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 01:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_auto_20170117_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='webhook',
            field=models.URLField(blank=True, null=True),
        ),
    ]