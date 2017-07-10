"""
Release: 0.1
Author: Golikov Ivan
Date: 10.07.2017
"""

from django.apps import AppConfig
from django.db.models import signals


class JournalConfig(AppConfig):
    name = 'journal'
    verbose_name = 'Журнал'

    def ready(self):
        import journal.signals as journal_signals

        from .models import Cabinet, CrossPoint, PBXPort, PunchBlock, Phone, Room, Subscriber

        signals.post_save.connect(journal_signals.pbxport_post_save, sender=PBXPort)

        signals.pre_save.connect(journal_signals.on_crosspoint_pre_change, sender=PunchBlock)
        signals.pre_save.connect(journal_signals.on_crosspoint_pre_change, sender=Phone)
        signals.pre_delete.connect(journal_signals.on_crosspoint_pre_change, sender=PunchBlock)
        signals.pre_delete.connect(journal_signals.on_crosspoint_pre_change, sender=Phone)

        signals.post_save.connect(journal_signals.on_crosspoint_post_change, sender=PunchBlock)
        signals.post_save.connect(journal_signals.on_crosspoint_post_change, sender=Phone)

        signals.post_save.connect(journal_signals.on_crosspoint_post_change, sender=CrossPoint)

        signals.post_delete.connect(journal_signals.on_crosspoint_post_change, sender=CrossPoint)

        signals.post_save.connect(journal_signals.autocreate_location, sender=Cabinet)
        signals.post_save.connect(journal_signals.autocreate_location, sender=Room)

        signals.m2m_changed.connect(journal_signals.subscriber_phones_changed, sender=Subscriber.phones.through)
