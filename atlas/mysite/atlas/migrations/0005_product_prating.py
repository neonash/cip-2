# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-01 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0004_auto_20170531_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='pRating',
            field=models.DecimalField(decimal_places=1, default=1, max_digits=2),
            preserve_default=False,
        ),
    ]
