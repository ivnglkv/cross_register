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

from .models import Location, Phone


class LocationsFilter(admin.SimpleListFilter):
    title = 'Расположение'
    parameter_name = 'location'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        unique_locations_pks = qs.values_list('location').distinct()

        unique_locations = Location.objects.filter(
            pk__in=unique_locations_pks
        ).prefetch_related(
            'room').prefetch_related(
            'cabinet__room__building')

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
        if self.value() is not None:
            get_empty = True if self.value() == '0' else False
            queryset = queryset.filter(main_source__pbxport__isnull=get_empty)

        return queryset


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
