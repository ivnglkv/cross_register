# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-09 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0005_auto_20170709_0229'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpunchblock',
            name='char_number',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='номер'),
        ),
        migrations.AddField(
            model_name='punchblock',
            name='char_number',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='номер'),
        ),
    ]