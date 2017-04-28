from django.contrib import admin

from .models import (
    Building,
    Cabinet,
    Extension,
    Location,
    PBX,
    PBXPort,
    Phone,
    Room,
    Subscriber,
    Trunk,
)


admin.site.register(
    [Building,
     Cabinet,
     Extension,
     Location,
     PBX,
     PBXPort,
     Phone,
     Room,
     Subscriber,
     Trunk,
     ]
)
