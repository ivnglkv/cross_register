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

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .admin_filters import EmptyPBXPortsFilter, EmptyPunchBlocksFilter, LocationsFilter
from .forms import (
    ExtensionBoxForm,
    PunchBlockForm,
    PhoneForm,
    PBXForm,
    PBXPortForm,
    RoomForm,
    PBXRoomForm,
    SubscriberForm,
    CabinetForm,
)
from .models import (
    Building,
    Cabinet,
    ExtensionBox,
    PBX,
    PBXPort,
    PBXRoom,
    Phone,
    PunchBlock,
    PunchBlockType,
    Room,
    Subscriber,
)


admin.site.register(
    [Building,
     PunchBlockType,
     ],
    admin_class=SimpleHistoryAdmin,
)


def update_json_path(modeladmin, request, queryset):
    for pbx_port in queryset:
        pbx_port.update_json(save_without_historical_record=True)
update_json_path.short_description = 'Обновить отображение в журнале'


@admin.register(PunchBlock)
class PunchBlockAdmin(SimpleHistoryAdmin):
    form = PunchBlockForm
    list_filter = (
        EmptyPunchBlocksFilter,
        LocationsFilter,
    )
    search_fields = [
        '=number',
    ]
    list_per_page = 100

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        qs = qs.prefetch_related(
            'main_source').prefetch_related(
            'location__cabinet').prefetch_related(
            'type').prefetch_related(
            )

        return qs


@admin.register(Phone)
class PhoneAdmin(SimpleHistoryAdmin):
    form = PhoneForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        qs = qs.prefetch_related(
            'main_source').prefetch_related(
            'source__type').prefetch_related(
            'source__location__cabinet')

        return qs


@admin.register(PBX)
class PBXAdmin(SimpleHistoryAdmin):
    form = PBXForm


@admin.register(PBXPort)
class PBXPortAdmin(SimpleHistoryAdmin):
    form = PBXPortForm
    actions = [
        update_json_path,
    ]
    list_filter = (
        EmptyPBXPortsFilter,
        'pbx',
    )
    search_fields = (
        '=subscriber_number',
        'description',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        qs = qs.prefetch_related('pbx')

        return qs


@admin.register(Room)
class RoomAdmin(SimpleHistoryAdmin):
    form = RoomForm
    search_fields = [
        'room',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        qs = qs.prefetch_related('building')

        return qs


@admin.register(Subscriber)
class SubscriberAdmin(SimpleHistoryAdmin):
    form = SubscriberForm
    search_fields = (
        'last_name',
    )


@admin.register(PBXRoom)
class PBXRoomAdmin(SimpleHistoryAdmin):
    form = PBXRoomForm


@admin.register(Cabinet)
class CabinetAdmin(SimpleHistoryAdmin):
    form = CabinetForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        qs = qs.prefetch_related('room__building')

        return qs


@admin.register(ExtensionBox)
class ExtensionBoxAdmin(SimpleHistoryAdmin):
    form = ExtensionBoxForm

    search_fields = [
        '=box_number',
    ]
    list_filter = (
        'location__room__building',
    )
