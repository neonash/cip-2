# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-17 10:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0034_social'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataDictMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_filename', models.TextField()),
                ('dict_filename', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TaggedData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_filename', models.TextField()),
                ('rid', models.CharField(max_length=255)),
                ('dim1', models.TextField(blank=True, null=True)),
                ('d1_l1', models.TextField(blank=True, null=True)),
                ('d1_l2', models.TextField(blank=True, null=True)),
                ('d1_l3', models.TextField(blank=True, null=True)),
                ('d1_l4', models.TextField(blank=True, null=True)),
                ('d1_l5', models.TextField(blank=True, null=True)),
                ('dim2', models.TextField(blank=True, null=True)),
                ('d2_l1', models.TextField(blank=True, null=True)),
                ('d2_l2', models.TextField(blank=True, null=True)),
                ('d2_l3', models.TextField(blank=True, null=True)),
                ('d2_l4', models.TextField(blank=True, null=True)),
                ('d2_l5', models.TextField(blank=True, null=True)),
                ('dim3', models.TextField(blank=True, null=True)),
                ('d3_l1', models.TextField(blank=True, null=True)),
                ('d3_l2', models.TextField(blank=True, null=True)),
                ('d3_l3', models.TextField(blank=True, null=True)),
                ('d3_l4', models.TextField(blank=True, null=True)),
                ('d3_l5', models.TextField(blank=True, null=True)),
                ('dim4', models.TextField(blank=True, null=True)),
                ('d4_l1', models.TextField(blank=True, null=True)),
                ('d4_l2', models.TextField(blank=True, null=True)),
                ('d4_l3', models.TextField(blank=True, null=True)),
                ('d4_l4', models.TextField(blank=True, null=True)),
                ('d4_l5', models.TextField(blank=True, null=True)),
                ('dim5', models.TextField(blank=True, null=True)),
                ('d5_l1', models.TextField(blank=True, null=True)),
                ('d5_l2', models.TextField(blank=True, null=True)),
                ('d5_l3', models.TextField(blank=True, null=True)),
                ('d5_l4', models.TextField(blank=True, null=True)),
                ('d5_l5', models.TextField(blank=True, null=True)),
                ('dim6', models.TextField(blank=True, null=True)),
                ('d6_l1', models.TextField(blank=True, null=True)),
                ('d6_l2', models.TextField(blank=True, null=True)),
                ('d6_l3', models.TextField(blank=True, null=True)),
                ('d6_l4', models.TextField(blank=True, null=True)),
                ('d6_l5', models.TextField(blank=True, null=True)),
                ('dim7', models.TextField(blank=True, null=True)),
                ('d7_l1', models.TextField(blank=True, null=True)),
                ('d7_l2', models.TextField(blank=True, null=True)),
                ('d7_l3', models.TextField(blank=True, null=True)),
                ('d7_l4', models.TextField(blank=True, null=True)),
                ('d7_l5', models.TextField(blank=True, null=True)),
                ('dim8', models.TextField(blank=True, null=True)),
                ('d8_l1', models.TextField(blank=True, null=True)),
                ('d8_l2', models.TextField(blank=True, null=True)),
                ('d8_l3', models.TextField(blank=True, null=True)),
                ('d8_l4', models.TextField(blank=True, null=True)),
                ('d8_l5', models.TextField(blank=True, null=True)),
                ('dim9', models.TextField(blank=True, null=True)),
                ('d9_l1', models.TextField(blank=True, null=True)),
                ('d9_l2', models.TextField(blank=True, null=True)),
                ('d9_l3', models.TextField(blank=True, null=True)),
                ('d9_l4', models.TextField(blank=True, null=True)),
                ('d9_l5', models.TextField(blank=True, null=True)),
                ('dim10', models.TextField(blank=True, null=True)),
                ('d10_l1', models.TextField(blank=True, null=True)),
                ('d10_l2', models.TextField(blank=True, null=True)),
                ('d10_l3', models.TextField(blank=True, null=True)),
                ('d10_l4', models.TextField(blank=True, null=True)),
                ('d10_l5', models.TextField(blank=True, null=True)),
                ('dim11', models.TextField(blank=True, null=True)),
                ('d11_l1', models.TextField(blank=True, null=True)),
                ('d11_l2', models.TextField(blank=True, null=True)),
                ('d11_l3', models.TextField(blank=True, null=True)),
                ('d11_l4', models.TextField(blank=True, null=True)),
                ('d11_l5', models.TextField(blank=True, null=True)),
                ('dim12', models.TextField(blank=True, null=True)),
                ('d12_l1', models.TextField(blank=True, null=True)),
                ('d12_l2', models.TextField(blank=True, null=True)),
                ('d12_l3', models.TextField(blank=True, null=True)),
                ('d12_l4', models.TextField(blank=True, null=True)),
                ('d12_l5', models.TextField(blank=True, null=True)),
                ('dim13', models.TextField(blank=True, null=True)),
                ('d13_l1', models.TextField(blank=True, null=True)),
                ('d13_l2', models.TextField(blank=True, null=True)),
                ('d13_l3', models.TextField(blank=True, null=True)),
                ('d13_l4', models.TextField(blank=True, null=True)),
                ('d13_l5', models.TextField(blank=True, null=True)),
                ('dim14', models.TextField(blank=True, null=True)),
                ('d14_l1', models.TextField(blank=True, null=True)),
                ('d14_l2', models.TextField(blank=True, null=True)),
                ('d14_l3', models.TextField(blank=True, null=True)),
                ('d14_l4', models.TextField(blank=True, null=True)),
                ('d14_l5', models.TextField(blank=True, null=True)),
                ('dim15', models.TextField(blank=True, null=True)),
                ('d15_l1', models.TextField(blank=True, null=True)),
                ('d15_l2', models.TextField(blank=True, null=True)),
                ('d15_l3', models.TextField(blank=True, null=True)),
                ('d15_l4', models.TextField(blank=True, null=True)),
                ('d15_l5', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
