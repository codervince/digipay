# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-24 00:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_transaction_is_emailed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
