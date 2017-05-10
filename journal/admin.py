from django.contrib import admin

from .forms import PunchBlockForm
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
     PBXPort,
     PBXRoom,
     Phone,
     Room,
     Subscriber,
     ]
)


@admin.register(PunchBlock)
class PunchBlockAdmin(admin.ModelAdmin):
    form = PunchBlockForm
