# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-16 11:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0030_social'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Social',
        ),
    ]