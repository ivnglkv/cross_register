"""
Release: 0.1.5
Author: Golikov Ivan
Date: 17.07.2017
"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .admin_filters import LocationsFilter
from .forms import (
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
    list_filter = (LocationsFilter,)
    list_per_page = 30


@admin.register(Phone)
class PhoneAdmin(SimpleHistoryAdmin):
    form = PhoneForm


@admin.register(PBX)
class PBXAdmin(SimpleHistoryAdmin):
    form = PBXForm


@admin.register(PBXPort)
class PBXPortAdmin(SimpleHistoryAdmin):
    form = PBXPortForm
    actions = [
        update_json_path,
    ]


@admin.register(Room)
class RoomAdmin(SimpleHistoryAdmin):
    form = RoomForm


@admin.register(Subscriber)
class SubscriberAdmin(SimpleHistoryAdmin):
    form = SubscriberForm


@admin.register(PBXRoom)
class PBXRoomAdmin(SimpleHistoryAdmin):
    form = PBXRoomForm


@admin.register(Cabinet)
class CabinetAdmin(SimpleHistoryAdmin):
    form = CabinetForm
