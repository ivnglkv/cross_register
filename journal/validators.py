# This file is part of Cregister - cross register management software
# Copyright (C) 2017  Golikov Ivan <ivnglkv@eml.cc>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.core.exceptions import ValidationError

from .models import CrossPoint


def validate_crosspoint(value):
    if not issubclass(type(value), CrossPoint):
        raise ValidationError('В качестве точки, откуда приходит линия, '
                              'указан несуществующий плинт или телефон')
