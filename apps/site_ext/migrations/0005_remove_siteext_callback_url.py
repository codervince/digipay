# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 01:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('site_ext', '0004_auto_20170111_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteext',
            name='callback_url',
        ),
    ]
