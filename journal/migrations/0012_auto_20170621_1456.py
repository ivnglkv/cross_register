# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-21 11:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('journal', 'transfer_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalpunchblock',
            name='type',
        ),
        migrations.RemoveField(
            model_name='punchblock',
            name='type',
        ),
    ]
