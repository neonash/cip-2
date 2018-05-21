# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-16 07:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0026_tagdicts'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagdicts',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tagdicts',
            name='dict_filename',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tagdicts',
            name='ngram',
            field=models.CharField(max_length=255),
        ),
    ]