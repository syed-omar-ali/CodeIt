# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-25 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_synced'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='synced',
            name='problems',
        ),
        migrations.AddField(
            model_name='synced',
            name='data',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='synced',
            name='memory',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='synced',
            name='problem',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='synced',
            name='time',
            field=models.CharField(default='', max_length=10),
        ),
    ]
