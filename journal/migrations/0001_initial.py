# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 16:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=5, unique=True, verbose_name='номер')),
                ('letter', models.CharField(blank=True, max_length=2, verbose_name='литера')),
            ],
            options={
                'verbose_name': 'корпус',
                'verbose_name_plural': 'корпуса',
            },
        ),
        migrations.CreateModel(
            name='Cabinet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=15, unique=True, verbose_name='номер')),
            ],
            options={
                'verbose_name': 'шкаф',
                'verbose_name_plural': 'шкафы',
            },
        ),
        migrations.CreateModel(
            name='CrossPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cabinet', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='journal.Cabinet', verbose_name='шкаф')),
            ],
            options={
                'verbose_name': 'расположение',
                'verbose_name_plural': 'расположения',
            },
        ),
        migrations.CreateModel(
            name='PBX',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manufacturer', models.CharField(choices=[('asterisk', 'Asterisk'), ('avaya', 'Avaya'), ('m-200', 'М-200'), ('multicom', 'Мультиком'), ('panasonic', 'Panasonic')], max_length=10, verbose_name='производитель')),
                ('model', models.CharField(max_length=40, verbose_name='модель')),
            ],
            options={
                'verbose_name': 'АТС',
                'verbose_name_plural': 'АТС',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.CharField(max_length=45, verbose_name='помещение')),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='journal.Building', verbose_name='корпус')),
            ],
            options={
                'verbose_name': 'помещение',
                'verbose_name_plural': 'помещения',
            },
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='имя')),
                ('last_name', models.CharField(max_length=40, verbose_name='фамилия')),
                ('patronymic', models.CharField(blank=True, max_length=35, verbose_name='отчество')),
            ],
            options={
                'verbose_name': 'абонент',
                'verbose_name_plural': 'абоненты',
            },
        ),
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('crosspoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='journal.CrossPoint')),
                ('number', models.SmallIntegerField(verbose_name='номер')),
            ],
            options={
                'verbose_name': 'распределение',
                'verbose_name_plural': 'распределения',
            },
            bases=('journal.crosspoint',),
        ),
        migrations.CreateModel(
            name='PBXPort',
            fields=[
                ('crosspoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='journal.CrossPoint')),
                ('number', models.CharField(blank=True, max_length=20, verbose_name='номер порта')),
                ('type', models.CharField(choices=[('sip', 'SIP'), ('analog', 'Аналоговый'), ('pri', 'E1')], default='analog', max_length=10, verbose_name='тип порта')),
                ('subscriber_number', models.PositiveSmallIntegerField(blank=True, null=True, unique=True, verbose_name='абонентский номер')),
                ('description', models.CharField(blank=True, max_length=150, verbose_name='описание')),
                ('pbx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.PBX', verbose_name='АТС')),
            ],
            options={
                'verbose_name': 'порт АТС',
                'verbose_name_plural': 'порты АТС',
            },
            bases=('journal.crosspoint',),
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('crosspoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='journal.CrossPoint')),
            ],
            options={
                'verbose_name': 'телефон',
                'verbose_name_plural': 'телефоны',
            },
            bases=('journal.crosspoint',),
        ),
        migrations.CreateModel(
            name='Trunk',
            fields=[
                ('crosspoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='journal.CrossPoint')),
                ('number', models.SmallIntegerField(verbose_name='номер')),
            ],
            options={
                'verbose_name': 'магистраль',
                'verbose_name_plural': 'магистрали',
            },
            bases=('journal.crosspoint',),
        ),
        migrations.AddField(
            model_name='location',
            name='room',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='journal.Room', verbose_name='помещение'),
        ),
        migrations.AddField(
            model_name='crosspoint',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incoming', to='journal.CrossPoint', verbose_name='направление'),
        ),
        migrations.AddField(
            model_name='crosspoint',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.Location', verbose_name='расположение'),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.Room', verbose_name='расположение'),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='phone',
            field=models.ManyToManyField(related_name='subscribers', to='journal.Phone', verbose_name='телефоны'),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('building', 'room')]),
        ),
    ]
