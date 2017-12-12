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

from django.apps import AppConfig
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)


class JournalConfig(AppConfig):
    name = 'journal'
    verbose_name = 'Журнал'

    def ready(self):
        from journal.signals import (
            autocreate_location,
            on_crosspoint_post_change,
            on_crosspoint_pre_change,
            pbxport_post_save,
            subscriber_phones_changed,
            subscriber_post_changed,
            subscriber_pre_changed,
        )

        from .models import (
            Cabinet,
            CrossPoint,
            ExtensionBox,
            PBXPort,
            Phone,
            PunchBlock,
            Room,
            Subscriber,
        )

        post_save.connect(pbxport_post_save, sender=PBXPort)

        crosspoints_classes = [
            ExtensionBox,
            Phone,
            PunchBlock,
        ]

        locations_classes = [
            Cabinet,
            Room,
        ]

        # Сигналы от точек кросса
        multiple_connect(pre_save, on_crosspoint_pre_change, crosspoints_classes)
        multiple_connect(post_save, on_crosspoint_post_change, crosspoints_classes)
        multiple_connect(pre_delete, on_crosspoint_pre_change, crosspoints_classes)
        post_delete.connect(on_crosspoint_post_change, sender=CrossPoint)

        # Сигналы от расположений
        multiple_connect(post_save, autocreate_location, locations_classes)

        # Сигналы от абонента
        pre_save.connect(subscriber_pre_changed, sender=Subscriber)
        post_save.connect(subscriber_post_changed, sender=Subscriber)
        pre_delete.connect(subscriber_pre_changed, sender=Subscriber)
        post_delete.connect(subscriber_post_changed, sender=Subscriber)
        m2m_changed.connect(subscriber_phones_changed, sender=Subscriber.phones.through)


def multiple_connect(signal, handler, senders):
    """Соединение одного сигнала от нескольких отправителей с одним обработчиком

    Parameters
    ----------
    signal : Signal
        Сигнал, к которому нужно присоединить получателей
    handler : func
        Функция-обработчик сигнала
    senders : iterable
        Список отправителей
    """

    for sender in senders:
        signal.connect(handler, sender=sender)
