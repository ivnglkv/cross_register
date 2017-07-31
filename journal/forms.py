"""
Release: 0.2.2
Author: Golikov Ivan
Date: 24.07.2017
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
    ExtensionBox,
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
            Q(room__pbxroom__isnull=False)).prefetch_related(
            'room__building').prefetch_related(
            'cabinet__room__building'),
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
            'jack',
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
    phones_queryset = Phone.objects.filter(
            source__punchblock__isnull=False).filter(
            source__pbxport__isnull=False).prefetch_related(
            'main_source').prefetch_related(
            'source__type').prefetch_related(
            'source__location__cabinet').prefetch_related(
            'location__cabinet')

    phones = ModelMultipleChosenField(
        label='Телефоны',
        queryset=phones_queryset,
        required=False,
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


class ExtensionBoxForm(ModelForm):
    location = ModelChosenField(
        label='Расположение',
        queryset=Location.objects.filter(
            Q(room__isnull=False) &
            Q(room__pbxroom__isnull=True)
        ).prefetch_related('room__building').all()
    )
    source = CrosspointField(label='Откуда приходит',
                             required=False)

    class Meta:
        model = ExtensionBox
        fields = [
            'location',
            'source',
            'box_number',
            'pair_number',
        ]
