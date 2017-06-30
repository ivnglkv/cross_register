from django.apps import AppConfig
from django.db.models import signals


class JournalConfig(AppConfig):
    name = 'journal'
    verbose_name = 'Журнал'

    def ready(self):
        import journal.signals as journal_signals

        from .models import CrossPoint, PBXPort, PunchBlock, Phone

        signals.post_save.connect(journal_signals.pbxport_post_save, sender=PBXPort)

        signals.pre_save.connect(journal_signals.crosspoint_pre_save, sender=PunchBlock)
        signals.pre_save.connect(journal_signals.crosspoint_pre_save, sender=Phone)

        signals.post_save.connect(journal_signals.crosspoint_post_save, sender=PunchBlock)
        signals.post_save.connect(journal_signals.crosspoint_post_save, sender=Phone)

        signals.post_save.connect(journal_signals.crosspoint_post_save, sender=CrossPoint)
