# This file is part of Cregister - cross register management software
# Copyright (C) 2017  Golikov Ivan <ivnglkv@eml.cc>
#
# Cregister is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cregister is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cregister.  If not, see <http://www.gnu.org/licenses/>.

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
    PBXPortType,
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
            'cabinet__room__building').prefetch_related(
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
    type = ModelChosenField(
        label='Тип',
        queryset=PBXPortType.objects.all(),
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
            Q(room__pbxroom__isnull=False)
        ).prefetch_related(
            'cabinet__room__building').prefetch_related(
            'room__building'),
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
    phones_queryset = Phone.objects.prefetch_related(
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
            'building'),
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
        ).prefetch_related('room__building'),
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
