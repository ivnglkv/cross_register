from django.contrib import admin

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
    Room,
    Subscriber,
)


admin.site.register(
    [Building,
     Cabinet,
     Location,
     PBX,
     PBXRoom,
     Room,
     Subscriber,
     ]
)


@admin.register(PunchBlock)
class PunchBlockAdmin(admin.ModelAdmin):
    form = PunchBlockForm


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    form = PhoneForm


@admin.register(PBXPort)
class PBXPortAdmin(admin.ModelAdmin):
    form = PBXPortForm
