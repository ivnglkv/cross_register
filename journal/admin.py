from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .forms import (
    PunchBlockForm,
    PhoneForm,
    PBXPortForm,
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


admin.site.register(
    [Building,
     Cabinet,
     Location,
     PBX,
     PBXRoom,
     PunchBlockType,
     Room,
     Subscriber,
     ],
    admin_class=SimpleHistoryAdmin,
)


@admin.register(PunchBlock)
class PunchBlockAdmin(SimpleHistoryAdmin):
    form = PunchBlockForm


@admin.register(Phone)
class PhoneAdmin(SimpleHistoryAdmin):
    form = PhoneForm


@admin.register(PBXPort)
class PBXPortAdmin(SimpleHistoryAdmin):
    form = PBXPortForm
