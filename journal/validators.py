from django.core.exceptions import ValidationError

from .models import CrossPoint


def validate_crosspoint(value):
    if not issubclass(type(value), CrossPoint):
        raise ValidationError('В качестве точки, откуда приходит линия, '
                              'указан несуществующий плинт или телефон')
