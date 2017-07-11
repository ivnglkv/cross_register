"""
Release: 0.1
Author: Golikov Ivan
Date: 10.07.2017
"""

from django.forms import ModelForm
from django.db.models import Q

from .fields import (
    ChosenField,
    CrosspointField,
    ModelChosenField,
)
from .models import (
    Location,
    PBX,
    PBXPort,
    Phone,
    PunchBlock,
    PunchBlockType,
)


class PunchBlockForm(ModelForm):
    type = ModelChosenField(
        label='Тип',
        queryset=PunchBlockType.objects.all(),
    )
    location = ModelChosenField(
        label='Расположение',
        queryset=Location.objects.filter(
            Q(cabinet__isnull=False) |
            Q(room__pbxroom__isnull=False)),
    )
    source = CrosspointField(label='Откуда приходит',
                             required=False,
                             )

    class Meta:
        model = PunchBlock
        fields = [
            'type',
            'location',
            'source',
            'number',
            'is_station',
        ]


class PhoneForm(ModelForm):
    location = ModelChosenField(
        label='Расположение',
        queryset=Location.objects.filter(
            Q(room__isnull=False)),
    )
    source = CrosspointField(label='Откуда приходит',
                             required=False,
                             )

    class Meta:
        model = Phone
        fields = [
            'location',
            'source',
        ]


class PBXPortForm(ModelForm):
    pbx = ModelChosenField(
        label='АТС',
        queryset=PBX.objects.all(),
    )
    type = ChosenField(
        label='Тип',
        choices=PBXPort.PORT_TYPES,
        initial=PBXPort._meta.get_field('type').default,
    )

    class Meta:
        model = PBXPort
        fields = [
            'pbx',
            'number',
            'type',
            'subscriber_number',
            'description',
        ]


class PBXForm(ModelForm):
    manufacturer = ChosenField(
        label='Производитель',
        choices=PBX.MANUFACTURERS,
    )
    location = ModelChosenField(
        label='Расположение',
        queryset=Location.objects.filter(
            Q(cabinet__isnull=False) |
            Q(room__pbxroom__isnull=False)),
    )

    class Meta:
        model = PBX
        fields = [
            'manufacturer',
            'model',
            'location',
            'description',
        ]
