from django.contrib import admin

from .models import (
    Building,
    Cabinet,
    Location,
    PBX,
    PBXPort,
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
     Phone,
     PunchBlock,
     Room,
     Subscriber,
     ]
)
