"""
Release: 0.2.2
Author: Golikov Ivan
Date: 31.07.2017
"""

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

        # По неизвестной мне причине, метод append в данном месте возвращает None
        # В консоли всё хорошо
        ext_crosspoints_classes = crosspoints_classes + [CrossPoint]

        locations_classes = [
            Cabinet,
            Room,
        ]

        # Сигналы от точек кросса
        multiple_connect(pre_save, on_crosspoint_pre_change, crosspoints_classes)
        multiple_connect(post_save, on_crosspoint_post_change, ext_crosspoints_classes)
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
