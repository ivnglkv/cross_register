from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .forms import (
    PunchBlockForm,
    PhoneForm,
    PBXForm,
    PBXPortForm,
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
     Cabinet,
     PBXRoom,
     PunchBlockType,
     Room,
     Subscriber,
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
