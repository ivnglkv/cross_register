# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-16 23:22
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import F, Q


def populate_crosspoints_levels(apps, schema_editor):
    CrossPoint = apps.get_model('journal', 'CrossPoint')

    level_1_punchblocks = CrossPoint.objects.filter(
        Q(source__isnull=False) &
        Q(main_source_id=F('source'))
    )

    for pb in level_1_punchblocks:
        pb.level = 1
        pb.save()

    level_2_plus_points = CrossPoint.objects.filter(
        source__isnull=False).exclude(pk__in=level_1_punchblocks)

    for pb in level_2_plus_points:
        pb.level = pb.source.level + 1
        pb.save()


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0018_auto_20170717_0221'),
    ]

    operations = [
        migrations.RunPython(populate_crosspoints_levels),
    ]