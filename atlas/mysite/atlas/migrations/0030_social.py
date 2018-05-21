# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-16 11:03
from __future__ import unicode_literals

from django.db import migrations, models
import django_unixdatetimefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0029_tagdicts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Social',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_filename', models.TextField()),
                ('rid', models.CharField(max_length=255)),
                ('rTitle', models.TextField(blank=True, null=True)),
                ('rUser', models.TextField(blank=True, null=True)),
                ('rText', models.TextField(blank=True, null=True)),
                ('rURL', models.TextField(blank=True, null=True)),
                ('MEDIA_PROVIDER', models.TextField(blank=True, null=True)),
                ('rDate', django_unixdatetimefield.fields.UnixDateTimeField(blank=True, null=True)),
                ('rDate2', models.DateField(blank=True, null=True)),
                ('VIEW_COUNT', models.IntegerField(blank=True, null=True)),
                ('COMMENT_COUNT', models.IntegerField(blank=True, null=True)),
                ('UNIQUE_COMMENTERS', models.IntegerField(blank=True, null=True)),
                ('ENGAGEMENT', models.IntegerField(blank=True, null=True)),
                ('LINKS_AND_VOTES', models.IntegerField(blank=True, null=True)),
                ('INBOUND_LINKS', models.IntegerField(blank=True, null=True)),
                ('FORUM_THREAD_SIZE', models.IntegerField(blank=True, null=True)),
                ('FOLLOWING', models.IntegerField(blank=True, null=True)),
                ('FOLLOWERS', models.IntegerField(blank=True, null=True)),
                ('UPDATES', models.IntegerField(blank=True, null=True)),
                ('BLOG_POST_SENTIMENT', models.CharField(blank=True, max_length=45, null=True)),
            ],
        ),
    ]
