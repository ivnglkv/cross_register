from django.apps import AppConfig
from django.db.models import signals

import journal.signals as journal_signals


class JournalConfig(AppConfig):
    name = 'journal'
    verbose_name = 'Журнал'

    def ready(self):
        from .models import PBXPort

        signals.post_save.connect(journal_signals.pbxport_post_save, sender=PBXPort)
