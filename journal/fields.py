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

import re

from django.core.exceptions import ObjectDoesNotExist
from django.forms.fields import CharField, ChoiceField
from django.forms import (
    ModelChoiceField,
    ModelMultipleChoiceField,
    Select,
    SelectMultiple,
)

from .models import CrossPoint, PBXPort, PunchBlock, PunchBlockType
from .validators import validate_crosspoint


class CrosspointField(CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.validators.append(validate_crosspoint)

    def prepare_value(self, value):
        result = ''

        try:
            if type(value) != int:
                raise AssertionError

            result = CrossPoint.objects.get(pk=value).journal_str()
        except ObjectDoesNotExist:
            result = super().prepare_value(value)
        except (ValueError, AssertionError):
            # При возникновении ошибки на этапе сохранения (например, ValidationError)
            # в поле будет передана строка с введенным значением
            result = value

        return result

    def to_python(self, value):
        result = None

        value = ''.join(value.split())

        if len(value) == 0:
            return result

        punchblock_types = PunchBlockType.objects.all()
        patterns_types_list = []

        for pb_type in punchblock_types:
            patterns_types_list.append((re.compile(pb_type.regexp), pb_type))

        for pattern_type in patterns_types_list:
            match = pattern_type[0].match(value)

            if match:
                pb_type = pattern_type[1]

                if (pb_type.is_station_group is not None and
                        match.group(pb_type.is_station_group) is not None):
                    pb_is_station = True
                else:
                    pb_is_station = False

                pb_number = match.group(pb_type.number_group)
                pb_location = match.group(pb_type.location_group)

                try:
                    result = PunchBlock.objects.get(type=pb_type,
                                                    is_station=pb_is_station,
                                                    number=pb_number,
                                                    location__cabinet__number=pb_location)
                except ObjectDoesNotExist:
                    pass

        if not result and re.match(r'^\d{3,7}$', value):
            phone_number = int(value)

            try:
                result = PBXPort.objects.get(subscriber_number=phone_number)
            except ObjectDoesNotExist:
                pass

        return result

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)

        return value


class ChosenField(ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = Select(attrs={'class': 'chosen-select'})

        super().__init__(*args, **kwargs)


class ModelChosenField(ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = Select(attrs={'class': 'chosen-select'})

        super().__init__(*args, **kwargs)


class ModelMultipleChosenField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = SelectMultiple(attrs={'class': 'chosen-select'})

        super().__init__(*args, **kwargs)
