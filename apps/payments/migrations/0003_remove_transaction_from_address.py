# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-11 01:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_transaction_payment_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='from_address',
        ),
    ]
