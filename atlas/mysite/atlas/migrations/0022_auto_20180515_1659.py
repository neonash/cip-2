# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-15 11:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0021_auto_20180515_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='dimenmap',
            name='dict_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dimenmap',
            name='dict_filename',
            field=models.CharField(max_length=100),
        ),
    ]
