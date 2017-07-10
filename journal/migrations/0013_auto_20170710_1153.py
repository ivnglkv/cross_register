# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-10 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0012_auto_20170710_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpbx',
            name='description',
            field=models.CharField(blank=True, help_text='Подразделение, которое обслуживает АТС', max_length=30, verbose_name='примечание'),
        ),
        migrations.AlterField(
            model_name='pbx',
            name='description',
            field=models.CharField(blank=True, help_text='Подразделение, которое обслуживает АТС', max_length=30, verbose_name='примечание'),
        ),
    ]
