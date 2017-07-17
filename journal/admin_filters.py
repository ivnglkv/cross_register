"""
Release: 0.1.5
Author: Golikov Ivan
Date: 17.07.2017
"""

from django.contrib import admin

from .models import Location


class LocationsFilter(admin.SimpleListFilter):
    title = 'Расположение'
    parameter_name = 'location'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        unique_locations_pks = qs.values_list('location').distinct()

        unique_locations = Location.objects.filter(pk__in=unique_locations_pks)

        for location in unique_locations:
            yield (str(location.pk), str(location))

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(location_id=int(self.value()))
