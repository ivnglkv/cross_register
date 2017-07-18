"""
Release: 0.1.5
Author: Golikov Ivan
Date: 18.07.2017
"""

from django.contrib import admin

from .models import Location, Phone


class LocationsFilter(admin.SimpleListFilter):
    title = 'Расположение'
    parameter_name = 'location'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        unique_locations_pks = qs.values_list('location').distinct()

        unique_locations = Location.objects.filter(pk__in=unique_locations_pks)

        for location in unique_locations:
            yield (location.pk, location)

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(location_id=self.value())


class EmptyPunchBlocksFilter(admin.SimpleListFilter):
    title = 'Занятость'
    parameter_name = 'empty'

    def lookups(self, request, model_admin):
        return (
            (0, 'Свободные'),
            (1, 'Занятые'),
        )

    def queryset(self, request, queryset):
        get_empty = True if self.value() == '0' else False

        return queryset.filter(main_source__pbxport__isnull=get_empty)


class EmptyPBXPortsFilter(admin.SimpleListFilter):
    title = 'Занятость'
    parameter_name = 'ports_empty'

    def lookups(self, request, model_admin):
        return (
            (0, 'Свободные'),
        )

    def queryset(self, request, queryset):
        get_empty = True if self.value() == '0' else False

        if get_empty:
            phones = Phone.objects.filter(main_source__isnull=False)
            exclude_list = [x.main_source_id for x in phones]

            queryset = queryset.exclude(pk__in=exclude_list)

        return queryset