"""
Release: 0.1.5
Author: Golikov Ivan
Date: 19.07.2017
"""

from django.forms import ModelForm
from django.db.models import Q

from .fields import (
    ChosenField,
    CrosspointField,
    ModelChosenField,
    ModelMultipleChosenField,
)
from .models import (
    Building,
    Cabinet,
    Location,
    PBX,
    PBXPort,
    PBXRoom,
    Phone,
    PunchBlock,
    PunchBlockType,
    Room,
    Subscriber,
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
            Q(room__isnull=False)).order_by('-id').prefetch_related(
            'cabinet').prefetch_related(
            'cabinet__room').prefetch_related(
            'cabinet__room__building').prefetch_related(
            'room').prefetch_related(
            'room__building'),
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


class RoomForm(ModelForm):
    building = ModelChosenField(
        label='Корпус',
        queryset=Building.objects.all(),
    )

    class Meta:
        model = Room
        fields = [
            'building',
            'room',
        ]


class SubscriberForm(ModelForm):
    phones = ModelMultipleChosenField(
        label='Телефоны',
        queryset=Phone.objects.prefetch_related(
            'main_source').prefetch_related(
            'source').prefetch_related(
            'source__location__cabinet').prefetch_related(
            'source__type').prefetch_related(
            'location__cabinet').all(),
    )

    class Meta:
        model = Subscriber
        fields = [
            'first_name',
            'last_name',
            'patronymic',
            'phones',
        ]


class PBXRoomForm(ModelForm):
    room = ModelChosenField(
        label='Помещение',
        queryset=Room.objects.all(),
    )

    class Meta:
        model = PBXRoom
        fields = [
            'room',
        ]


class CabinetForm(ModelForm):
    room = ModelChosenField(
        label='Расположение',
        queryset=Room.objects.prefetch_related(
            'building').all(),
    )

    class Meta:
        model = Cabinet
        fields = [
            'room',
            'number',
        ]
