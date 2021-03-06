# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-06 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0027_pbxporttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpbxport',
            name='type_tmp',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='journal.PBXPortType'),
        ),
        migrations.AddField(
            model_name='pbxport',
            name='type_tmp',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='journal.PBXPortType', verbose_name='тип порта'),
            preserve_default=False,
        ),
    ]
