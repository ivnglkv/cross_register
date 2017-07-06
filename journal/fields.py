import re

from django.core.exceptions import ObjectDoesNotExist
from django.forms.fields import CharField
from django.forms import ValidationError

from .models import CrossPoint, PBXPort, PunchBlock, PunchBlockType


class CrosspointField(CharField):
    def prepare_value(self, value):
        result = ''

        if re.match('\d+', str(value)):
            id = value
            result = CrossPoint.objects.get(pk=id).journal_str()
        else:
            result = super().prepare_value(value)

        return result

    def clean(self, value):
        result = None

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

                if match.group(pb_type.is_station_group) is not None:
                    pb_is_station = True
                else:
                    pb_is_station = False

                pb_number = int(match.group(pb_type.number_group))
                pb_location = match.group(pb_type.location_group)

                try:
                    result = PunchBlock.objects.get(type=pb_type,
                                                    is_station=pb_is_station,
                                                    number=pb_number,
                                                    location__cabinet__number=pb_location)
                except ObjectDoesNotExist:
                    pass

        if not result and re.match(r'^\d{4}$', value):
            phone_number = int(value)

            try:
                result = PBXPort.objects.get(subscriber_number=phone_number)
            except ObjectDoesNotExist:
                pass

        if not result:
            raise ValidationError('В качестве точки, откуда приходит линия, '
                                  'указан несуществующий плинт или телефон')

        return result
